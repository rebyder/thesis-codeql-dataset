# repo: mccorkle/seds-utils
# path: Sbs.py

class Sbs:

    def __init__(self, sbsFilename, sbc_filename, newSbsFilename):

        import xml.etree.ElementTree as ET
        import Sbc

        self.mySbc = Sbc.Sbc(sbc_filename)
        self.sbsTree = ET.parse(sbsFilename)
        self.sbsRoot = self.sbsTree.getroot()

        self.XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"

        self.newSbsFilename = newSbsFilename

    def findPlayerBySteamID(self, steam_id):
        if (steam_id == 0):
            return False

        print("looking for player with steamID of %s" % steam_id)

        ourPlayerDict = self.mySbc.getPlayerDict()

        for player in ourPlayerDict:
            # print playerDict[player]['steamID']
            if ourPlayerDict[player]['steamID'] == steam_id:
                return ourPlayerDict[player]

        # if we don't find the user
        return False

    def giveReward(self, rewardOwner, rewardType, rewardAmount):
        """
        This method will hunt down the first cargo container owned by
        <Owner> matching their ingame ID, and with with "CustomName"
        of "LOOT" and place the rewards in it
        """

        import xml.etree.ElementTree as ET

        print("trying to give %s %s units of %s" % (rewardOwner, rewardAmount, rewardType))

        for sectorObjects in self.sbsRoot.iter('SectorObjects'):
            for entityBase in sectorObjects.iter('MyObjectBuilder_EntityBase'):
                # EntityId = entityBase.find('EntityId')
                # print ("checking entityID %s" % EntityId.text)
                gridSize = entityBase.find('GridSizeEnum')

                # TODO+: some kind of warning if we have a reward to give, but can't find this user's LOOT container
                if hasattr(gridSize, 'text'):
                    cubeBlocks = entityBase.find('CubeBlocks')
                    for myCubeBlock in cubeBlocks.iter('MyObjectBuilder_CubeBlock'):
                        owner = myCubeBlock.find("Owner")
                        EntityId = myCubeBlock.find('EntityId')
                        customName = myCubeBlock.find('CustomName')
                        if hasattr(owner, 'text') and owner.text == rewardOwner and myCubeBlock.get(self.XSI_TYPE) == "MyObjectBuilder_CargoContainer" and hasattr(customName, 'text'):
                            if "LOOT" in customName.text:
                                print("I found a cargo container owned by %s with entityID of %s and name of %s" % (owner.text, EntityId.text, customName.text))
                                componentContainer = myCubeBlock.find('ComponentContainer')
                                components = componentContainer.find('Components')
                                componentData = components.find('ComponentData')
                                component = componentData.find('Component')
                                items = component.find('Items')
                                itemCount = 0
                                for myInventoryItems in items.iter('MyObjectBuilder_InventoryItem'):
                                    itemCount += 1

                                print("planning to add %s of %s into it as item %s" % (rewardAmount, rewardType, itemCount))
                                # <MyObjectBuilder_InventoryItem>
                                #   <Amount>200</Amount>
                                #   <PhysicalContent xsi:type="MyObjectBuilder_Ore">
                                #     <SubtypeName>Uranium</SubtypeName>  ## from rewardType
                                #   </PhysicalContent>
                                #   <ItemId>4</ItemId>  ## from itemCount
                                #   <AmountDecimal>200</AmountDecimal>  ## from rewardAmount
                                # </MyObjectBuilder_InventoryItem>
                                # myCubeBlock.append((ET.fromstring('<MyObjectBuilder_InventoryItem><Amount>123456789</Amount></MyObjectBuilder_InventoryItem>')))
                                inventoryItem = ET.SubElement(items, 'MyObjectBuilder_InventoryItem')
                                amount = ET.SubElement(inventoryItem, 'Amount')
                                amount.text = str(rewardAmount)
                                physicalContent = ET.SubElement(inventoryItem, 'PhysicalContent')
                                physicalContent.set(self.XSI_TYPE, 'MyObjectBuilder_Ore')
                                subtypeName = ET.SubElement(physicalContent, 'SubtypeName')
                                subtypeName.text = rewardType
                                itemId = ET.SubElement(inventoryItem, 'ItemId')
                                itemId.text = str(itemCount)
                                amountDecimal = ET.SubElement(inventoryItem, 'AmountDecimal')
                                amountDecimal.text = str(rewardAmount)
                                nextItemId = component.find('nextItemId')
                                nextItemId.text = str(itemCount + 1)
                                # FIXME: this makes a mess of the html, figure out a way to clean it up?

    def removeFloaters(self):

        import xml.etree.ElementTree as ET

        removedCount = 0
        warnCount = 0

        for sectorObjects in self.sbsRoot.iter('SectorObjects'):
            for entityBase in sectorObjects.iter('MyObjectBuilder_EntityBase'):
                cubeGridID = entityBase.find('EntityId')
                gridSizeEnum = entityBase.find('GridSizeEnum')
                objectType = entityBase.get(self.XSI_TYPE)
                isStatic = entityBase.find('IsStatic')  # FIXME: this does not do what I thought it did. Tested with simple station, and it isn't set as static when I build it from scratch.
                # TODO: only way I can see to easily fix is check for <Forward x="-0" y="-0" z="-1" /> for static things
                # print cubeGridID.text if hasattr(cubeGridID, 'text') else  'not defined'
                if hasattr(cubeGridID, 'text'):
                    print("Grid EntityID: %s " % cubeGridID.text)
                else:
                    print("FIXME: no gridID")

                # print ("\t is objectType %s" % objectType )

                if hasattr(isStatic, 'text'):
                    # this is a base, all of our checks are null and void.  Bases don't float or cost me CPU
                    print("\t skipping trash checks because this IsStatic")
                    continue

                if hasattr(gridSizeEnum, 'text'):
                    # is a grid, small or large
                    gridName = entityBase.find('DisplayName').text
                    print("\t is a grid size %s %s" % (gridSizeEnum.text, gridName))
                    # if the name contains DEL.WRN
                    if "[DEL.WRN]" in gridName:
                        print("\t ALREADY HAD DEL.WRN in the NAME, GOODBYE")
                        sectorObjects.remove(entityBase)
                        removedCount += 1
                    else:
                        # it doesn't have a DEL WRN yet, lets check for our rules
                        # TODO: look through the whole entityBase for 6 thrusters, a power supply, and at least one block not owned by pirates
                        thrusterCount = 0
                        powerSource = 0
                        controlSurface = 0
                        gyroCount = 0
                        turretCount = 0
                        ownerCount = 0
                        ownedThings = 0
                        ownerList = []

                        cubeBlocks = entityBase.find('CubeBlocks')
                        for myCubeBlock in cubeBlocks.iter('MyObjectBuilder_CubeBlock'):
                            owner = myCubeBlock.find("Owner")
                            # subtype = myCubeBlock.find('SubtypeName')
                            cubeType = myCubeBlock.get(self.XSI_TYPE)
                            entityID = myCubeBlock.find("EntityId")

                            # print ("\t\tTODO: cubeType of: %s" % cubeType)
                            if "Thrust" in cubeType:
                                thrusterCount += 1
                            elif "Cockpit" in cubeType:
                                controlSurface += 1
                            elif "Reactor" in cubeType:
                                powerSource += 1
                            elif "SolarPanel" in cubeType:
                                powerSource += 1
                            elif "RemoteControl" in cubeType:
                                controlSurface += 1
                            elif "Gyro" in cubeType:
                                gyroCount += 1
                            elif "Turret" in cubeType:
                                turretCount += 1

                            if hasattr(owner, 'text'):
                                # print ("\tOwner: %s" % owner.text)
                                if owner.text not in ownerList:
                                    ownerList.append(owner.text)
                                    ownerCount += 1
                                ownedThings += 1  # TODO: this is how many blocks have an owner, above is distinct owners of this grid

                        print("\t totals: %s %s %s %s %s %s %s" % (thrusterCount, powerSource, controlSurface, gyroCount, turretCount, ownerCount, len(ownerList)))
                        # TODO: if it fails all my tests,

                        # [CHECK] set name to [DEL.WRN]
                        # set ShowOnHUD to True ## can't, this is per cube.  Ignore this.

                        if (thrusterCount < 6 or controlSurface < 1 or powerSource < 1 or gyroCount < 1 or ownerCount < 1):
                            print("\tWARNING: THIS GRID IS DUE TO DELETE")
                            gridNameToUpdate = entityBase.find('DisplayName')
                            gridNameToUpdate.text = "[DEL.WRN]" + gridNameToUpdate.text
                            print("\tname is now: %s" % gridNameToUpdate.text)
                            warnCount += 1
                            for myCubeBlock in cubeBlocks.iter('MyObjectBuilder_CubeBlock'):
                                # set all DeformationRatio to 1 (right up under owner) <DeformationRatio>0.5</DeformationRatio>
                                deformationElement = ET.SubElement(myCubeBlock, "DeformationRatio")
                                deformationElement.text = ".77"
                                # myCubeBlock.append('DeformationRatio', '.77')
                else:
                    if (objectType == "MyObjectBuilder_FloatingObject"):
                        print("\t GOODBYE")
                        sectorObjects.remove(entityBase)
                        removedCount += 1

                    elif (objectType == "MyObjectBuilder_ReplicableEntity"):
                        # print ("\t Backpack!")
                        backPackName = entityBase.find('Name')
                        if hasattr(backPackName, 'text'):
                            print("\t Backpackname: %s" % backPackName.text)
                            print("\t GOODBYE")
                            sectorObjects.remove(entityBase)
                            removedCount += 1

                    elif (objectType == "MyObjectBuilder_VoxelMap"):
                        voxelStorageName = entityBase.find('StorageName')
                        if hasattr(voxelStorageName, 'text'):
                            print("\t voxelStorageName: %s" % voxelStorageName.text)

                    elif (objectType == "MyObjectBuilder_Character"):
                        # oops, someone was online
                        # entityID matches CharacterEntityId in the sbc
                        entityID = entityBase.find('EntityId').text  # steamID
                        print("\t looking for %s entityID in playerDict" % entityID)
                        thisPlayersDict = self.findPlayerBySteamID(entityID)  # returns False if we didn't have this players steamID in the sbc, meaning they weren't online

                        if (thisPlayersDict is not False and entityID is not False):
                            print("\t Sorry player: %s %s" % (entityID, thisPlayersDict["username"]))
                        else:
                            print("\tFIXME: this player was online, but I don't have their steamID of %s in the sbc" % entityID)
                    else:
                        print("\t ##### has no grid size")

        # print ("writing tree out to %s" % newSbsFileName)
        # tree = ET.ElementTree(sbsRoot)
        # sbsRoot.attrib["xmlns:xsd"]="http://www.w3.org/2001/XMLSchema"
        # tree.write(newSbsFileName, encoding='utf-8', xml_declaration=True)

        return (removedCount, warnCount)

    def writeFile(self):

        import xml.etree.ElementTree as ET

        print("writing tree out to %s" % self.newSbsFilename)
        tree = ET.ElementTree(self.sbsRoot)
        self.sbsRoot.attrib["xmlns:xsd"] = "http://www.w3.org/2001/XMLSchema"
        tree.write(self.newSbsFilename, encoding='utf-8', xml_declaration=True)
