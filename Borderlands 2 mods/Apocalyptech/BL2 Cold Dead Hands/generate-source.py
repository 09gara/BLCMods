#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright (c) 2018, CJ Kucera
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the development team nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL CJ KUCERA BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys

try:
    from hotfixes import Hotfixes
except ModuleNotFoundError:
    print('')
    print('****************************************************************')
    print('To run this script, you will need to copy or symlink hotfixes.py')
    print('from the parent directory, so it exists here as well.  Sorry for')
    print('the bother!')
    print('****************************************************************')
    print('')
    sys.exit(1)

###
### Output variables
###

mod_name = 'BL2 Cold Dead Hands'
mod_version = '1.0.0-prerelease'
output_filename = '{}-source.txt'.format(mod_name)

###
### Some constants
###

class BaseConfig(object):
    """
    Basic class to hold config info
    """

    def __format__(self, formatstr):
        """
        A bit of magic so that we can use our values in format strings
        """
        attr = getattr(self, formatstr)
        if type(attr) == str:
            return attr
        elif type(attr) == int or type(attr) == float:
            return str(attr)
        else:
            return attr()

class OtherConfig(BaseConfig):
    """
    Config which isn't specific to our other drops
    """

    # Some text that we'll put into the main file
    disable_world_sets = None

    # Adding things to the legendary pools
    legendary_unique_adds = None
    legendary_pearl_adds = None
    legendary_seraph_adds = None

    # Pools used to provide proper weighted equipment drops for bosses.
    # These will be all set via Hotfix, and re-used by enemies in different
    # levels.  That way, we only need as many pools as we have loot-dropping
    # bosses in a single level.
    level_pool_0 = 'GD_CustomItemPools_allium.Mercenary.AlliumXmasSkins'
    level_pool_1 = 'GD_CustomItemPools_allium.Psycho.AlliumXmasSkins'
    level_pool_2 = 'GD_CustomItemPools_allium.Siren.AlliumXmasSkins'

class DropConfig(BaseConfig):
    """
    Class to hold basic config for drops
    """

    # Base drop probabilities.  These will be altered slightly for the weighted
    # drop pools.
    drop_prob_pistols = 100
    drop_prob_ar = 100
    drop_prob_smg = 100
    drop_prob_shotguns = 100
    drop_prob_snipers = 80
    drop_prob_launchers = 40

    # Scale for weighted pools
    weight_scale = 2.5

    ###
    ### Statements which'll be filled in later
    ###

    # Rarity pools for regular enemies
    set_rarity_ar = None
    set_rarity_launchers = None
    set_rarity_pistols = None
    set_rarity_shotguns = None
    set_rarity_smg = None
    set_rarity_snipers = None

    # Equip pools for regular enemies
    set_equip_all = None
    set_equip_ar = None
    set_equip_launchers = None
    set_equip_pistols = None
    set_equip_shotguns = None
    set_equip_smg = None
    set_equip_snipers = None
    set_equip_only_shotguns = None

    # Shield pool (only need to worry about one pool for these)
    set_shields = None

    # Rarity weight presets that we'll generate
    weight_common = None
    weight_uncommon = None
    weight_rare = None
    weight_veryrare = None
    weight_alien = None
    weight_legendary = None
    rarity_presets = [
            ('excellent', 'Enemies Have Excellent Gear'),
            ('better', 'Enemies Have Better Gear'),
            ('stock', 'Enemies Have Roughly Stock Gear'),
        ]

    # Computed percent drop rates, for reporting to the user in mod comments
    pct_common = None
    pct_uncommon = None
    pct_rare = None
    pct_veryrare = None
    pct_alien = None
    pct_legendary = None
    
    ###
    ### ... FUNCTIONS??!?
    ###

    def __init__(self, hotfixes):
        self.hotfixes = hotfixes
        self.num_hotfixes = 0

    def _single_assignment_hotfix(self, prefix, classname, attribute, pool, level=None):
        """
        A single assignment hotfix.  Convenience function just to avoid repetition.
        Returns the hotfix XML which should be output in the mod file.
        """
        if level is None:
            level = ''
        hotfix_id = '{}_{}'.format(self.hotfix_prefix, self.num_hotfixes)
        self.hotfixes.add_level_hotfix(hotfix_id, 'EnemyDrop',
                "{},{},{},,ItemPoolDefinition'{}'".format(
                    level, classname, attribute, pool))
        self.num_hotfixes += 1
        return '{}{}'.format(prefix, self.hotfixes.get_hotfix(hotfix_id).get_xml())

    def hotfix_assignments(self):
        """
        Returns a string of rendered hotfixes for performing our custom item pool
        assignments.
        """

        retlist = []
        prefix = ' ' * (4*4)

        # The order in which our assignment tuples are specified
        pool_order = [
                self.equip_pool_ar,
                self.equip_pool_pistols,
                self.equip_pool_shotguns,
                self.equip_pool_smg,
                self.equip_pool_all,
                self.equip_pool_launchers,
                self.equip_pool_snipers,
                self.equip_pool_only_shotguns,
                self.pool_shields,
            ]

        # First, assign enemies using DefaultItemPoolList[x]
        for (pool, classlist) in zip(pool_order, self.enemy_dipl):
            for (dipl_idx, classname) in classlist:
                retlist.append(self._single_assignment_hotfix(
                    prefix,
                    classname,
                    'DefaultItemPoolList[{}].ItemPool'.format(dipl_idx),
                    pool))

        # Next, enemies using PlayThroughs[x].CustomItemPoolList[y]
        for (pool, classlist) in zip(pool_order, self.enemy_pt_cipl):
            for (pt_idx, cipl_idx, classname) in classlist:
                retlist.append(self._single_assignment_hotfix(
                    prefix,
                    classname,
                    'PlayThroughs[{}].CustomItemPoolList[{}].ItemPool'.format(
                        pt_idx, cipl_idx),
                    pool))

        # Next, enemies using ItemPoolList[x] in a specific level WillowAIPawn
        for (pool, classlist) in zip(pool_order, self.enemy_level_ipl):
            for (level, ipl_idx, classname) in classlist:
                retlist.append(self._single_assignment_hotfix(
                    prefix,
                    classname,
                    'ItemPoolList[{}].ItemPool'.format(ipl_idx),
                    pool,
                    level=level))

        # Next, enemies using DefaultLoot[x].ItemAttachments[y]
        for (pool, classlist) in zip(pool_order, self.enemy_dl_ia):
            for (dl_idx, ia_idx, classname) in classlist:
                retlist.append(self._single_assignment_hotfix(
                    prefix,
                    classname,
                    'DefaultLoot[{}].ItemAttachments[{}].ItemPool'.format(
                        dl_idx, ia_idx),
                    pool))

        # Next, enemies using NewItemPoolList[0]
        for (pool, classlist) in zip(pool_order, self.enemy_nipl):
            for (nipl_idx, classname) in classlist:
                retlist.append(self._single_assignment_hotfix(
                    prefix,
                    classname,
                    'NewItemPoolList[{}].ItemPool'.format(nipl_idx),
                    pool))

        return "\n\n".join(retlist)

    def _get_pct_chance(self, weight, total):
        chance = weight/total*100
        if chance == 0:
            return '0'
        elif chance > 1:
            return round(chance)
        else:
            return round(chance, 2)


    def set_rarity_weights(self, rarity_key):
        rarity = self.rarities[rarity_key]
        self.weight_common = rarity['common']
        self.weight_uncommon = rarity['uncommon']
        self.weight_rare = rarity['rare']
        self.weight_veryrare = rarity['veryrare']
        self.weight_alien = rarity['alien']
        self.weight_legendary = rarity['legendary']

        total_weight = (self.weight_common + self.weight_uncommon +
                self.weight_rare + self.weight_veryrare +
                self.weight_alien + self.weight_legendary)

        self.pct_common = self._get_pct_chance(self.weight_common, total_weight)
        self.pct_uncommon = self._get_pct_chance(self.weight_uncommon, total_weight)
        self.pct_rare = self._get_pct_chance(self.weight_rare, total_weight)
        self.pct_veryrare = self._get_pct_chance(self.weight_veryrare, total_weight)
        self.pct_alien = self._get_pct_chance(self.weight_alien, total_weight)
        self.pct_legendary = self._get_pct_chance(self.weight_legendary, total_weight)

class Regular(DropConfig):
    """
    Config info for regular enemies
    """

    # Hotfix prefix
    hotfix_prefix = 'reg'

    # Equip weights
    rarities = {
        'excellent': {
            'common': 20,
            'uncommon': 85,
            'rare': 65,
            'veryrare': 40,
            'alien': 20,
            'legendary': 1,
            },
        'better': {
            'common': 32.75,
            'uncommon': 35,
            'rare': 25,
            'veryrare': 5,
            'alien': 2,
            'legendary': 0.25,
            },
        'stock': {
            'common': 100,
            'uncommon': 10,
            'rare': 1,
            'veryrare': 0.1,
            'alien': 0.1,
            'legendary': 0.01,
            },
        }

    # Rarity weight pools
    rarity_pool_ar = 'GD_CustomItemPools_MainGame.Soldier.TorgueUncommon'
    rarity_pool_launchers = 'GD_CustomItemPools_Lilac.Psycho.TorgueUncommon'
    rarity_pool_pistols = 'GD_CustomItemPools_MainGame.Mercenary.TorgueUncommon'
    rarity_pool_shotguns = 'GD_CustomItemPools_tulip.Mechro.TorgueUncommon'
    rarity_pool_smg = 'GD_CustomItemPools_MainGame.Siren.TorgueUncommon'
    rarity_pool_snipers = 'GD_CustomItemPools_MainGame.Assassin.TorgueUncommon'

    # Equip pools (this is where gun type weights are applied)
    equip_pool_all = 'GD_CustomItemPools_allium.Mechro.AlliumXmasSkins'
    equip_pool_ar = 'GD_CustomItemPools_MainGame.Soldier.VladofUncommon'
    equip_pool_launchers = 'GD_CustomItemPools_Lilac.Psycho.VladofUncommon'
    equip_pool_pistols = 'GD_CustomItemPools_MainGame.Mercenary.VladofUncommon'
    equip_pool_shotguns = 'GD_CustomItemPools_tulip.Mechro.VladofUncommon'
    equip_pool_smg = 'GD_CustomItemPools_MainGame.Siren.VladofUncommon'
    equip_pool_snipers = 'GD_CustomItemPools_MainGame.Assassin.VladofUncommon'
    equip_pool_only_shotguns = 'GD_CustomItemPools_allium.Assassin.AlliumXmasSkins'

    # Shield pool
    pool_shields = 'GD_CustomItemPools_allium.Mechro.AlliumTGSkins'

    ###
    ### Enemy changes
    ###

    enemy_dipl = (
            # ARs
            [
                (0, 'GD_Allium_LootMidget_LoaderJET.Balance.PawnBalance_LootMidget_LoaderJETAllium'),
                (0, 'GD_Allium_LootMidgetLoaderBUL.Balance.PawnBalance_LootMidget_LoaderBULAllium'),
                (0, 'GD_HolidayLoader.Balance.PawnBalance_HolidayLoader'),
                (0, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_MissionPlaceholder'),
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_BikeRiderMarauder'),
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_RaidBikeMarauder'),
                (0, 'GD_Iris_Population_Loader.Balance.Iris_PawnBalance_LoaderGUN'),
                (0, 'GD_Iris_Population_Rat.Balance.Iris_PawnBalance_RatTunnel'),
                (0, 'GD_Orchid_Hovercraft.AI.PawnBalance_Hovercraft_Rider'),
                (0, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderGUN'),
                (0, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderJunk'),
                (0, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderPirate'),
                (0, 'GD_Orchid_Pop_Loader.Disabled.Balance.PawnBalance_Orchid_LoaderGUN_Disabled'),
                (0, 'GD_Orchid_Pop_Loader.Disabled.Balance.PawnBalance_Orchid_LoaderJunk_Disabled'),
                (0, 'GD_Orchid_Pop_PirateRadioGuy.PawnBalance_Orchid_PirateRadioGuy'),
                (0, 'GD_Population_Goliath.Balance.PawnBalance_GoliathOneArm'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderGUN'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderJET'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderGUN'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderGUN_HealthCashAmmoOnly'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderJunk'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_TundraPatrol'),
                (1, 'GD_Population_Midget.Balance.PawnBalance_MidgetNomad'),
                (0, 'GD_RatGrunt_Digi.Population.PawnBalance_RatGrunt_Digi'),
                (0, 'GD_Sage_Pop_Loader.Balance.PawnBalance_Sage_LoaderGUN'),
                (0, 'GD_Population_Goliath.Balance.PawnBalance_Goliath'),
                (0, 'GD_Population_Goliath.Balance.PawnBalance_GoliathLootGoon'),
                (0, 'GD_Aster_Pop_Dwarves.Balance.PawnBalance_Dwarfzerker'),
                (0, 'GD_Aster_Pop_Dwarves.Balance.PawnBalance_Dwarfzerker_Minus2'),
                (0, 'GD_Aster_Pop_Dwarves.Balance.PawnBalance_Dwarfzerker_StandStill'),
                (0, 'GD_Aster_Pop_Orcs.Balance.PawnBalance_Orczerker'),
            ],
            # Pistols
            [
                (1, 'GD_Orchid_Hovercraft.AI.PawnBalance_Hovercraft_Rider'),
                (0, 'GD_Orchid_SM_JockoLegUp_Data.PawnBalance_Orchid_PiratePegLeg'),
                (0, 'GD_ResistanceFighter.Population.BD_ResistanceFighter_Pistol'), # Sure, make Sanctuary a bit more colorful
                (0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderIntro'),
                (0, 'GD_Population_Midget.Balance.PawnBalance_MidgetGoliath'),
            ],
            # Shotguns
            [
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_Bike'),
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_GrinderBike'),
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_RaidBike'),
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_RaidGrinderBike'),
                (0, 'GD_Iris_Population_Bruiser.Balance.Iris_PawnBalance_BikerBruiser'),
                (1, 'GD_Iris_Population_Marauder.Balance.Iris_PawnBalance_SullyTheStabber'),
                (0, 'GD_Iris_Population_Midget.Balance.Iris_PawnBalance_BikerMidget'),
                (0, 'GD_Nast_Hodunk_Grunt.Balance.PawnBalance_Nast_HodunkGrunt'),
                (0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateGrenadier'),
                (0, 'GD_Population_Goliath.Balance.PawnBalance_Juggernaught'),
                (0, 'GD_Population_Goliath.Balance.Unique.PawnBalance_DiggerGoliath'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_HodunkGrunt'),
            ],
            # SMGs
            [
                (0, 'GD_Iris_Population_Loader.Balance.Iris_PawnBalance_LoaderJET'),
                (0, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_ScarlettMarauder'),
                (0, 'GD_Population_Engineer.Balance.PawnBalance_EngyArms_FreeWilly_Skag'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderJET'),
                (0, 'GD_Population_Midget.Balance.PawnBalance_MidgetRat'),
                (0, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf1'),
                (0, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf2'),
                (0, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf3'),
                (0, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf4'),
                (0, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf5'),
                (0, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf6'),
                (0, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf7'),
                (0, 'GD_Sage_Pop_Natives.Balance.PawnBalance_Native_Soldier'),
                (1, 'GD_Nast_BadassJunkLoader.Population.PawnBalance_BadassJunkLoader'),
                (0, 'GD_Nast_Native_Soldier.Population.PawnBalance_Nast_Native_Soldier'),
                (0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMarauderSMG'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_ZafordGrunt'),
                (0, 'GD_Nast_Zaford_Grunt.Balance.PawnBalance_Nast_ZafordGroomsman'),
                (0, 'GD_Nast_Zaford_Grunt.Balance.PawnBalance_Nast_ZafordGrunt'),
            ],
            # All
            [
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_BikeRiderMidget'),
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_RaidBikeMidget'),
                (0, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BigBiker'),
                (0, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_Biker'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderSGT'),
                (0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMarauder'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderBUL'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderBUL'),
                (0, 'GD_Population_Loader.Balance.Unique.JackFight.PawnBalance_LoaderBUL_JackFight'),
                (0, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderBUL'),
                (0, 'GD_Orchid_Pop_Loader.Disabled.Balance.PawnBalance_Orchid_LoaderBUL_Disabled'),
            ],
            # Launchers
            [
                (1, 'GD_ButcherBoss3.Balance.PawnBalance_ButcherBoss3'),
                (0, 'GD_Iris_Population_Goliath.Balance.Iris_PawnBalance_ArenaGoliath'),
                (0, 'GD_Iris_Population_Loader.Balance.Iris_PawnBalance_LoaderRPG'),
                (0, 'GD_Iris_Population_MotorMama.Balance.Iris_PawnBalance_MotorMamaBike'),
                (0, 'GD_Orchid_Pop_Deserters.Deserter3.PawnBalance_Orchid_Deserter3'),
                (0, 'GD_Population_Goliath.Balance.PawnBalance_GoliathBlaster'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderRPG'),
                (0, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Rocket'),
            ],
            # Snipers
            [
                (0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateHunter'),
                (0, 'GD_Population_Engineer.Balance.PawnBalance_BlackOps'),
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
                (1, 'GD_Allium_LootMidget_LoaderJET.Balance.PawnBalance_LootMidget_LoaderJETAllium'),
                (1, 'GD_Allium_LootMidgetLoaderBUL.Balance.PawnBalance_LootMidget_LoaderBULAllium'),
                (1, 'GD_HolidayLoader.Balance.PawnBalance_HolidayLoader'),
                (2, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BigBiker'),
                (2, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_Biker'),
                (1, 'GD_Iris_Population_Goliath.Balance.Iris_PawnBalance_ArenaGoliath'),
                (0, 'GD_Iris_Population_Loader.Balance.Iris_PawnBalance_LoaderPWR'),
                (1, 'GD_Nast_Hodunk_Grunt.Balance.PawnBalance_Nast_HodunkGrunt'),
                (3, 'GD_Nast_Zaford_Grunt.Balance.PawnBalance_Nast_ZafordGroomsman'),
                (3, 'GD_Nast_Zaford_Grunt.Balance.PawnBalance_Nast_ZafordGrunt'),
                (3, 'GD_Nast_Zaford_Grunt.Balance.PawnBalance_Nast_ZafordKnife'),
                (3, 'GD_Orchid_Hovercraft.AI.PawnBalance_Hovercraft_Rider'),
                (0, 'GD_Orchid_Pop_BubblesLilSis.Balance.PawnBalance_Orchid_Bubbles'),
                (1, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderBUL'),
                (0, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderEXP'),
                (1, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderGUN'),
                (1, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderHOT'),
                (1, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderJunk'),
                (1, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderPirate'),
                (0, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderPWR'),
                (1, 'GD_Orchid_Pop_PirateRadioGuy.PawnBalance_Orchid_PirateRadioGuy'),
                (1, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateHunter'),
                (1, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMarauder'),
                (1, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_ScarlettMarauder'),
                (0, 'GD_Population_Constructor.Balance.Unique.PawnBalance_Constructor_1340'),
                (1, 'GD_Population_Engineer.Balance.PawnBalance_BlackOps'),
                (0, 'GD_Population_Engineer.Balance.Unique.PawnBalance_RequisitionOfficer'),
                (1, 'GD_Population_Goliath.Balance.PawnBalance_Juggernaught'),
                (1, 'GD_Population_Jack.Balance.PawnBalance_JackClone'),
                (1, 'GD_Population_Jack.Balance.PawnBalance_JackCloneMelee_Shield'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderBUL'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderEXP'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderGUN'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderHOT'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderION'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderJET'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderPWR'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_BunkerLoaderWAR'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderBUL'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderEXP'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderGUN'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderGUN_HealthCashAmmoOnly'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderHOT'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderION'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderION_HealthCashAmmoOnly'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderJET'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderJunk'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderLWT'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderPWR'),
                (2, 'GD_Population_Loader.Balance.PawnBalance_LoaderRPG'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderSGT'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderWAR'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderWAR_HealthCashAmmoOnly'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderWAR_Overlooked'),
                (1, 'GD_Population_Loader.Balance.Unique.JackFight.PawnBalance_LoaderBUL_JackFight'),
                (0, 'GD_Population_Loader.Balance.Unique.JackFight.PawnBalance_LoaderEXP_JackFight'),
                (1, 'GD_Population_Loader.Balance.Unique.JackFight.PawnBalance_LoaderGUN_JackFight'),
                (1, 'GD_Population_Marauder.Balance.Unique.PawnBalance_Ep13_Roland'),
                (1, 'GD_Population_Marauder.Balance.Unique.PawnBalance_Ep6_Roland'),
                (1, 'GD_Population_Marauder.Balance.Unique.PawnBalance_HodunkGrunt'),
                (3, 'GD_Population_Marauder.Balance.Unique.PawnBalance_ZafordGrunt'),
                (0, 'GD_Population_Midget.Balance.PawnBalance_MidgetNomad'),
                (1, 'GD_Population_Midget.Balance.PawnBalance_MidgetRat'),
                (1, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf1'),
                (1, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf2'),
                (1, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf3'),
                (1, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf4'),
                (1, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf5'),
                (1, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf6'),
                (1, 'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf7'),
                (1, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Rocket'),
                (0, 'GD_Population_Psycho.Balance.Unique.PawnBalance_Undertaker'),
                (0, 'GD_Population_Rat.Balance.PawnBalance_RatPlague'),
                (0, 'GD_Psycho_Digi.Population.PawnBalance_Psycho_Digi'),
                (0, 'GD_PsychoMidget_Digi.Population.PawnBalance_PsychoMidget_Digi'),
                (1, 'GD_RatGrunt_Digi.Population.PawnBalance_RatGrunt_Digi'),
                (0, 'GD_Sage_Pop_Loader.Balance.PawnBalance_Sage_LoaderEXP'),
                (1, 'GD_Sage_Pop_Loader.Balance.PawnBalance_Sage_LoaderGUN'),
                (1, 'GD_Sage_Pop_Loader.Balance.PawnBalance_Sage_LoaderION'),
            ],
        )

    enemy_pt_cipl = (
            # ARs
            [
                (0, 1, 'GD_Allium_Butcher_Midget.Balance.PawnBalance_ButcherMidget'),
                (1, 1, 'GD_Allium_Butcher_Midget.Balance.PawnBalance_ButcherMidget'),
                (2, 1, 'GD_Allium_Butcher_Midget.Balance.PawnBalance_ButcherMidget'),
                (0, 0, 'GD_Iris_Population_RaidPete.Balance.PawnBalance_Iris_RaidPete_SewerPipeRat'),
                (1, 0, 'GD_Iris_Population_Rat.Balance.Iris_PawnBalance_RatTunnel'),
                (0, 0, 'GD_Population_Engineer.Balance.PawnBalance_HyperionSoldier'),
                (1, 0, 'GD_Population_Engineer.Balance.PawnBalance_HyperionSoldier'),
                (0, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRider'),
                (1, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRider'),
                (0, 0, 'GD_Population_Marauder.Balance.PawnBalance_Scavenger'),
                (1, 1, 'GD_Population_Midget.Balance.PawnBalance_MidgetNomad'),
                (0, 0, 'GD_Population_Nomad.Balance.PawnBalance_Nomad'),
                (1, 0, 'GD_Population_Nomad.Balance.PawnBalance_Nomad'),
                (1, 0, 'GD_Population_Nomad.Balance.PawnBalance_NomadPyro'),
                (0, 0, 'GD_Population_Nomad.Balance.PawnBalance_NomadShieldwMidget'),
                (1, 0, 'GD_Population_Nomad.Balance.PawnBalance_NomadShieldwMidget'),
                (0, 0, 'GD_Population_Nomad.Balance.PawnBalance_NomadShock'),
                (1, 0, 'GD_Population_Nomad.Balance.PawnBalance_NomadShock'),
                (0, 0, 'GD_Population_Rat.Balance.PawnBalance_RatRider'),
                (0, 0, 'GD_Population_Rat.Balance.PawnBalance_RatTunnel'),
                (1, 0, 'GD_Population_Rat.Balance.PawnBalance_RatTunnel'),
                (0, 0, 'GD_Allium_GoliathSnow.Balance.PawnBalance_GoliathSnow'),
                (0, 0, 'GD_Allium_MarauderKitchen.Balance.PawnBalance_MarauderKitchen'),
                (1, 0, 'GD_Allium_MarauderKitchen.Balance.PawnBalance_MarauderKitchen'),
                (2, 0, 'GD_Allium_MarauderKitchen.Balance.PawnBalance_MarauderKitchen'),
                (0, 0, 'GD_Allium_MarauderSnow.Balance.PawnBalance_MarauderSnow'),
                (1, 0, 'GD_Allium_MarauderSnow.Balance.PawnBalance_MarauderSnow'),
                (2, 0, 'GD_Allium_MarauderSnow.Balance.PawnBalance_MarauderSnow'),
                (0, 0, 'GD_Nomad_Digi.Population.PawnBalance_Nomad_Digi'),
            ],
            # Pistols
            [
                (0, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderGrunt'),
            ],
            # Shotguns
            [
                (1, 0, 'GD_Iris_Population_Bruiser.Balance.Iris_PawnBalance_BikerBruiser'),
                (1, 0, 'GD_Iris_Population_Midget.Balance.Iris_PawnBalance_BikerMidget'),
                (0, 0, 'GD_Population_Bruiser.Balance.PawnBalance_Bruiser'),
                (1, 0, 'GD_Population_Bruiser.Balance.PawnBalance_Bruiser'),
                (0, 0, 'GD_Population_Bruiser.Balance.PawnBalance_Bruiser_LilithIntro'),
                (1, 0, 'GD_Population_Bruiser.Balance.PawnBalance_Bruiser_LilithIntro'),
                (0, 0, 'GD_Population_Engineer.Balance.PawnBalance_HyperionInfiltrator'),
                (1, 0, 'GD_Population_Engineer.Balance.PawnBalance_HyperionInfiltrator'),
                (0, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderElite'),
                (1, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderElite'),
                (1, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderGrunt'),
                (0, 0, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Taskmaster'),
                (1, 0, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Taskmaster'),
            ],
            # SMGs
            [
                (0, 0, 'GD_Population_Engineer.Balance.PawnBalance_Engineer'),
                (1, 0, 'GD_Population_Engineer.Balance.PawnBalance_Engineer'),
                (0, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderPsycho'),
                (1, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderPsycho'),
                (0, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRegular'),
                (1, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRegular'),
                (1, 0, 'GD_Population_Midget.Balance.PawnBalance_MidgetRat'),
                (0, 0, 'GD_Population_Rat.Balance.Unique.PawnBalance_ProspectorRat'),
                (1, 0, 'GD_Population_Rat.Balance.Unique.PawnBalance_ProspectorRat'),
                (0, 0, 'GD_MarauderRegular_Digi.Population.PawnBalance_MarauderRegular_Digi'),
                (0, 0, 'GD_Pop_HallowSkeleton.Balance.PawnBalance_BanditFireSkeleton'),
                (1, 0, 'GD_Pop_HallowSkeleton.Balance.PawnBalance_BanditFireSkeleton'),
                (2, 0, 'GD_Pop_HallowSkeleton.Balance.PawnBalance_BanditFireSkeleton'),
                (0, 0, 'GD_Pop_HallowSkeleton.Balance.PawnBalance_BanditHallowSkeleton'),
                (1, 0, 'GD_Pop_HallowSkeleton.Balance.PawnBalance_BanditHallowSkeleton'),
                (2, 0, 'GD_Pop_HallowSkeleton.Balance.PawnBalance_BanditHallowSkeleton'),
                (0, 1, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMarauderSMG'),
            ],
            # All
            [
                (1, 0, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BigBiker'),
                (1, 0, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_Biker'),
                (1, 1, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMarauder'),
            ],
            # Launchers
            [
                (0, 0, 'GD_Population_Engineer.Balance.PawnBalance_HyperionHawk'),
                (1, 0, 'GD_Population_Engineer.Balance.PawnBalance_HyperionHawk'),
            ],
            # Snipers
            [
            ],
            # Only Shotguns
            [
                (0, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMidgetShotgun'),
                (1, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMidgetShotgun'),
                (0, 0, 'GD_Population_Midget.Balance.PawnBalance_MidgetShotgun'),
                (1, 0, 'GD_Population_Midget.Balance.PawnBalance_MidgetShotgun'),
            ],
            # Shields
            [
                (0, 0, 'GD_Allium_Butcher_Midget.Balance.PawnBalance_ButcherMidget'),
                (1, 0, 'GD_Allium_Butcher_Midget.Balance.PawnBalance_ButcherMidget'),
                (2, 0, 'GD_Allium_Butcher_Midget.Balance.PawnBalance_ButcherMidget'),
                (0, 1, 'GD_Allium_GoliathSnow.Balance.PawnBalance_GoliathSnow'),
                (0, 1, 'GD_Allium_MarauderKitchen.Balance.PawnBalance_MarauderKitchen'),
                (1, 1, 'GD_Allium_MarauderKitchen.Balance.PawnBalance_MarauderKitchen'),
                (2, 1, 'GD_Allium_MarauderKitchen.Balance.PawnBalance_MarauderKitchen'),
                (0, 1, 'GD_Allium_MarauderSnow.Balance.PawnBalance_MarauderSnow'),
                (1, 1, 'GD_Allium_MarauderSnow.Balance.PawnBalance_MarauderSnow'),
                (2, 1, 'GD_Allium_MarauderSnow.Balance.PawnBalance_MarauderSnow'),
                (0, 0, 'GD_Allium_PsychoKitchen.Balance.PawnBalance_PsychoKitchen'),
                (1, 0, 'GD_Allium_PsychoKitchen.Balance.PawnBalance_PsychoKitchen'),
                (2, 0, 'GD_Allium_PsychoKitchen.Balance.PawnBalance_PsychoKitchen'),
                (0, 0, 'GD_Allium_PsychoSnow.Balance.PawnBalance_PsychoSnow'),
                (1, 0, 'GD_Allium_PsychoSnow.Balance.PawnBalance_PsychoSnow'),
                (2, 0, 'GD_Allium_PsychoSnow.Balance.PawnBalance_PsychoSnow'),
                (0, 0, 'GD_Allium_PsychoSnow_Midget.Balance.PawnBalance_PsychoSnow_Midget'),
                (1, 0, 'GD_Allium_PsychoSnow_Midget.Balance.PawnBalance_PsychoSnow_Midget'),
                (2, 0, 'GD_Allium_PsychoSnow_Midget.Balance.PawnBalance_PsychoSnow_Midget'),
                (0, 0, 'GD_Butcher.Balance.PawnBalance_Butcher'),
                (1, 0, 'GD_Butcher.Balance.PawnBalance_Butcher'),
                (2, 0, 'GD_Butcher.Balance.PawnBalance_Butcher'),
                (1, 0, 'GD_HodunkPsycho.Balance.PawnBalance_HodunkPsycho'),
                (2, 0, 'GD_HodunkPsycho.Balance.PawnBalance_HodunkPsycho'),
                (1, 2, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BigBiker'),
                (1, 2, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_Biker'),
                (1, 0, 'GD_Iris_Population_Engineer.Balance.Iris_PawnBalance_EngineerArms'),
                (1, 0, 'GD_Iris_Population_Engineer.Balance.Iris_PawnBalance_EngineerArmsNoJump'),
                (0, 1, 'GD_MarauderRegular_Digi.Population.PawnBalance_MarauderRegular_Digi'),
                (0, 1, 'GD_Nomad_Digi.Population.PawnBalance_Nomad_Digi'),
                (0, 0, 'GD_Nomad_HMG_Digi.Population.PawnBalance_Nomad_HMG_Digi'),
                (1, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMarauder'),
                (1, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMarauderSMG'),
                (0, 2, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMidgetShotgun'),
                (1, 2, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateMidgetShotgun'),
                (1, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PiratePsycho'),
                (1, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PiratePsychoMidget'),
                (0, 0, 'GD_Population_Constructor.Balance.PawnBalance_Constructor'),
                (1, 0, 'GD_Population_Constructor.Balance.PawnBalance_Constructor'),
                (0, 0, 'GD_Population_Constructor.Balance.Unique.PawnBalance_ConstructorWillhelm'),
                (1, 0, 'GD_Population_Constructor.Balance.Unique.PawnBalance_ConstructorWillhelm'),
                (0, 1, 'GD_Population_Engineer.Balance.PawnBalance_Engineer'),
                (1, 1, 'GD_Population_Engineer.Balance.PawnBalance_Engineer'),
                (0, 0, 'GD_Population_Engineer.Balance.PawnBalance_EngineerArms'),
                (1, 0, 'GD_Population_Engineer.Balance.PawnBalance_EngineerArms'),
                (0, 1, 'GD_Population_Engineer.Balance.PawnBalance_HyperionHawk'),
                (1, 1, 'GD_Population_Engineer.Balance.PawnBalance_HyperionHawk'),
                (0, 1, 'GD_Population_Engineer.Balance.PawnBalance_HyperionInfiltrator'),
                (1, 1, 'GD_Population_Engineer.Balance.PawnBalance_HyperionInfiltrator'),
                (0, 1, 'GD_Population_Engineer.Balance.PawnBalance_HyperionSoldier'),
                (1, 1, 'GD_Population_Engineer.Balance.PawnBalance_HyperionSoldier'),
                (0, 0, 'GD_Population_Goliath.Balance.PawnBalance_GoliathCorrosive'),
                (1, 0, 'GD_Population_Goliath.Balance.PawnBalance_GoliathCorrosive'),
                (0, 1, 'GD_Population_Goliath.Balance.PawnBalance_GoliathTurret'),
                (1, 1, 'GD_Population_Goliath.Balance.PawnBalance_GoliathTurret'),
                (0, 2, 'GD_Population_Marauder.Balance.PawnBalance_MarauderElite'),
                (1, 2, 'GD_Population_Marauder.Balance.PawnBalance_MarauderElite'),
                (0, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderGrunt'),
                (1, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderGrunt'),
                (0, 2, 'GD_Population_Marauder.Balance.PawnBalance_MarauderPsycho'),
                (1, 2, 'GD_Population_Marauder.Balance.PawnBalance_MarauderPsycho'),
                (0, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRegular'),
                (1, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRegular'),
                (0, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRider'),
                (1, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderRider'),
                (0, 2, 'GD_Population_Marauder.Balance.PawnBalance_Scavenger'),
                (1, 0, 'GD_Population_Midget.Balance.PawnBalance_FlamingMidget'),
                (1, 0, 'GD_Population_Midget.Balance.PawnBalance_MidgetNomad'),
                (1, 1, 'GD_Population_Midget.Balance.PawnBalance_MidgetRat'),
                (0, 2, 'GD_Population_Midget.Balance.PawnBalance_MidgetShotgun'),
                (1, 2, 'GD_Population_Midget.Balance.PawnBalance_MidgetShotgun'),
                (1, 0, 'GD_Population_Midget.Balance.PawnBalance_MidgetSuicide'),
                (1, 0, 'GD_Population_Midget.Balance.PawnBalance_PsychoMidget'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_Nomad'),
                (1, 1, 'GD_Population_Nomad.Balance.PawnBalance_Nomad'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Ambush'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Taskmaster'),
                (1, 1, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Taskmaster'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadPyro'),
                (1, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadPyro'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadShieldwMidget'),
                (1, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadShieldwMidget'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadShock'),
                (1, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadShock'),
                (1, 0, 'GD_Population_Psycho.Balance.PawnBalance_Psycho'),
                (1, 0, 'GD_Population_Psycho.Balance.PawnBalance_PsychoBurning'),
                (1, 0, 'GD_Population_Psycho.Balance.PawnBalance_PsychoSlag'),
                (1, 0, 'GD_Population_Psycho.Balance.PawnBalance_PsychoSnow'),
                (1, 1, 'GD_Population_Psycho.Balance.PawnBalance_PsychoSuicide'),
                (0, 0, 'GD_Population_Rat.Balance.PawnBalance_RatLab'),
                (1, 0, 'GD_Population_Rat.Balance.PawnBalance_RatLab'),
                (0, 0, 'GD_Population_Rat.Balance.PawnBalance_RatThief'),
                (1, 0, 'GD_Population_Rat.Balance.PawnBalance_RatThief'),
                (1, 1, 'GD_Population_Rat.Balance.PawnBalance_RatTunnel'),
                (0, 1, 'GD_Population_Rat.Balance.Unique.PawnBalance_ProspectorRat'),
                (1, 1, 'GD_Population_Rat.Balance.Unique.PawnBalance_ProspectorRat'),
                (1, 0, 'GD_PsychoMidget_Digi.Population.PawnBalance_PsychoMidget_Digi'),
                (0, 0, 'GD_RatChef.Balance.PawnBalance_RatChef'),
                (0, 0, 'GD_RatLab_Digi.Population.PawnBalance_RatLab_Digi'),
                (1, 0, 'GD_RatLab_Digi.Population.PawnBalance_RatLab_Digi'),
            ],
        )

    enemy_level_ipl = (
            # ARs
            [
                ('Dam_P', 8, 'dam_p.TheWorld:PersistentLevel.WillowAIPawn_20'),
                ('Damtop_P', 8, 'damtop_p.TheWorld:PersistentLevel.WillowAIPawn_19'),
                ('Fridge_P', 8, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_178'),
                ('Fridge_P', 8, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_179'),
                ('Fridge_P', 8, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_180'),
                ('Fridge_P', 8, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_181'),
                ('Fridge_P', 8, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_229'),
                ('icecanyon_p', 8, 'icecanyon_p.TheWorld:PersistentLevel.WillowAIPawn_72'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_102'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_105'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_108'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_362'),
                ('Orchid_Refinery_P', 8, 'Orchid_Refinery_P.TheWorld:PersistentLevel.WillowAIPawn_224'),
            ],
            # Pistols
            [
            ],
            # Shotguns
            [
                ('Grass_Cliffs_P', 7, 'Grass_Cliffs_P.TheWorld:PersistentLevel.WillowAIPawn_253'),
                ('Interlude_P', 8, 'Interlude_P.TheWorld:PersistentLevel.WillowAIPawn_12'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_101'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_109'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_111'),
                ('Orchid_ShipGraveyard_P', 7, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_200'),
                ('Orchid_ShipGraveyard_P', 7, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_203'),
                ('Orchid_ShipGraveyard_P', 7, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_248'),
            ],
            # SMGs
            [
                ('dam_p', 7, 'dam_p.TheWorld:PersistentLevel.WillowAIPawn_23'),
                ('damtop_p', 7, 'damtop_p.TheWorld:PersistentLevel.WillowAIPawn_17'),
                ('Fridge_P', 8, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_182'),
                ('Grass_Cliffs_P', 8, 'Grass_Cliffs_P.TheWorld:PersistentLevel.WillowAIPawn_208'),
                ('Grass_Cliffs_P', 8, 'Grass_Cliffs_P.TheWorld:PersistentLevel.WillowAIPawn_254'),
                ('SouthpawFactory_P', 7, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_161'),
                ('SouthpawFactory_P', 7, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_162'),
                ('SouthpawFactory_P', 7, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_163'),
                ('SouthpawFactory_P', 7, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_164'),
                ('SouthpawFactory_P', 7, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_210'),
                ('SouthpawFactory_P', 7, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_211'),
                ('SouthpawFactory_P', 7, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_295'),
                ('Orchid_ShipGraveyard_P', 9, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_199'),
                ('Orchid_ShipGraveyard_P', 9, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_201'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_232'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_233'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_234'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_236'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_238'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_240'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_242'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_244'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_245'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_246'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_11'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_12'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_14'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_17'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_19'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_21'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_23'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_7'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_8'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_9'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_187'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_188'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_189'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_191'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_193'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_195'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_197'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_199'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_200'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_184'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_185'),
                ('Luckys_P', 7, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_182'),
            ],
            # All
            [
                ('Iris_DL2_Interior_P', 7, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_106'),
                ('Iris_DL2_Interior_P', 7, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_363'),
                ('Orchid_SaltFlats_P', 9, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_230'),
            ],
            # Launchers
            [
            ],
            # Snipers
            [
                ('Orchid_SaltFlats_P', 8, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_228'),
                ('Orchid_SaltFlats_P', 8, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_229'),
                ('Orchid_ShipGraveyard_P', 8, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_202'),
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
                ('dam_p', 9, 'dam_p.TheWorld:PersistentLevel.WillowAIPawn_20'),
                ('dam_p', 8, 'dam_p.TheWorld:PersistentLevel.WillowAIPawn_22'),
                ('dam_p', 9, 'dam_p.TheWorld:PersistentLevel.WillowAIPawn_23'),
                ('damtop_p', 9, 'damtop_p.TheWorld:PersistentLevel.WillowAIPawn_17'),
                ('damtop_p', 8, 'damtop_p.TheWorld:PersistentLevel.WillowAIPawn_18'),
                ('damtop_p', 9, 'damtop_p.TheWorld:PersistentLevel.WillowAIPawn_19'),
                ('Fridge_P', 9, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_178'),
                ('Fridge_P', 9, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_179'),
                ('Fridge_P', 9, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_180'),
                ('Fridge_P', 9, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_182'),
                ('Fridge_P', 8, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_227'),
                ('Fridge_P', 9, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_229'),
                ('Grass_Cliffs_P', 9, 'Grass_Cliffs_P.TheWorld:PersistentLevel.WillowAIPawn_208'),
                ('Grass_Cliffs_P', 9, 'Grass_Cliffs_P.TheWorld:PersistentLevel.WillowAIPawn_253'),
                ('Grass_Cliffs_P', 9, 'Grass_Cliffs_P.TheWorld:PersistentLevel.WillowAIPawn_254'),
                ('icecanyon_p', 8, 'icecanyon_p.TheWorld:PersistentLevel.WillowAIPawn_71'),
                ('icecanyon_p', 9, 'icecanyon_p.TheWorld:PersistentLevel.WillowAIPawn_72'),
                ('Interlude_P', 9, 'Interlude_P.TheWorld:PersistentLevel.WillowAIPawn_12'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_104'),
                ('Iris_DL2_Interior_P', 9, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_106'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_107'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_110'),
                ('Iris_DL2_Interior_P', 9, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_363'),
                ('Iris_DL2_Interior_P', 8, 'Iris_DL2_Interior_P.TheWorld:PersistentLevel.WillowAIPawn_364'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_11'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_12'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_14'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_17'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_182'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_184'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_185'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_187'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_188'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_189'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_19'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_191'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_193'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_195'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_197'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_199'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_200'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_21'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_23'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_232'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_233'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_234'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_236'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_238'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_240'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_242'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_244'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_245'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_246'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_7'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_8'),
                ('Luckys_P', 10, 'Luckys_P.TheWorld:PersistentLevel.WillowAIPawn_9'),
                ('Orchid_SaltFlats_P', 9, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_228'),
                ('Orchid_SaltFlats_P', 9, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_229'),
                ('Orchid_SaltFlats_P', 8, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_230'),
                ('Orchid_SaltFlats_P', 8, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_231'),
                ('Orchid_SaltFlats_P', 8, 'Orchid_SaltFlats_P.TheWorld:PersistentLevel.WillowAIPawn_277'),
                ('Orchid_ShipGraveyard_P', 8, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_199'),
                ('Orchid_ShipGraveyard_P', 8, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_201'),
                ('Orchid_ShipGraveyard_P', 9, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_202'),
                ('Orchid_ShipGraveyard_P', 9, 'Orchid_ShipGraveyard_P.TheWorld:PersistentLevel.WillowAIPawn_203'),
                ('SouthpawFactory_P', 9, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_161'),
                ('SouthpawFactory_P', 9, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_162'),
                ('SouthpawFactory_P', 9, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_163'),
                ('SouthpawFactory_P', 9, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_164'),
                ('SouthpawFactory_P', 9, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_210'),
                ('SouthpawFactory_P', 9, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_211'),
                ('SouthpawFactory_P', 9, 'SouthpawFactory_P.TheWorld:PersistentLevel.WillowAIPawn_295'),
                ('TundraTrain_P', 12, 'TundraTrain_P.TheWorld:PersistentLevel.WillowAIPawn_40'),
                ('TundraTrain_P', 12, 'TundraTrain_P.TheWorld:PersistentLevel.WillowAIPawn_41'),
                ('icecanyon_p', 9, 'icecanyon_p.TheWorld:PersistentLevel.WillowAIPawn_69'),
                ('icecanyon_p', 9, 'icecanyon_p.TheWorld:PersistentLevel.WillowAIPawn_70'),
            ],
        )

    enemy_dl_ia = (
            # ARs
            [
                (0, 0, 'GD_Episode06Data.BalanceDefs.BD_Ep6_RolandGunOnGround'),
            ],
            # Pistols
            [
            ],
            # Shotguns
            [
            ],
            # SMGs
            [
            ],
            # "All but Launchers"
            [
            ],
            # Launchers
            [
            ],
            # Snipers
            [
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
            ],
        )

    enemy_nipl = (
            # ARs
            [
            ],
            # Pistols
            [
            ],
            # Shotguns
            [
            ],
            # SMGs
            [
            ],
            # All
            [
                (0, 'GD_Sage_ClaptrapWorshipper.Character.AIDef_Sage_ClaptrapWorshiper:AIBehaviorProviderDefinition_0.Behavior_AIChangeInventory_29'),
            ],
            # Launchers
            [
            ],
            # Snipers
            [
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
            ],
        )

class Badass(DropConfig):
    """
    Config info for badass enemies
    """

    # Hotfix prefix
    hotfix_prefix = 'badass'

    # Equip weights
    rarities = {
        'excellent': {
            'common': 0,
            'uncommon': 0,
            'rare': 35,
            'veryrare': 60,
            'alien': 55,
            'legendary': 10,
            },
        'better': {
            'common': 0,
            'uncommon': 25,
            'rare': 49,
            'veryrare': 15,
            'alien': 10,
            'legendary': 1,
            },
        # There's really not such a thing as a "stock" badass pool we could
        # base these weights on, so we're sort of just making it up.
        'stock': {
            'common': 0,
            'uncommon': 40,
            'rare': 30,
            'veryrare': 20,
            'alien': 10,
            'legendary': 0.25,
            },
        }

    # Rarity weight pools
    rarity_pool_ar = 'GD_CustomItemPools_MainGame.Soldier.TorgueEpic'
    rarity_pool_launchers = 'GD_CustomItemPools_Lilac.Psycho.TorgueEpic'
    rarity_pool_pistols = 'GD_CustomItemPools_MainGame.Mercenary.TorgueEpic'
    rarity_pool_shotguns = 'GD_CustomItemPools_tulip.Mechro.TorgueEpic'
    rarity_pool_smg = 'GD_CustomItemPools_MainGame.Siren.TorgueEpic'
    rarity_pool_snipers = 'GD_CustomItemPools_MainGame.Assassin.TorgueEpic'

    # Equip pools (this is where gun type weights are applied)
    equip_pool_all = 'GD_CustomItemPools_allium.Mechro.AlliumXmasHeads'
    equip_pool_ar = 'GD_CustomItemPools_MainGame.Soldier.VladofEpic'
    equip_pool_launchers = 'GD_CustomItemPools_Lilac.Psycho.VladofEpic'
    equip_pool_pistols = 'GD_CustomItemPools_MainGame.Mercenary.VladofEpic'
    equip_pool_shotguns = 'GD_CustomItemPools_tulip.Mechro.VladofEpic'
    equip_pool_smg = 'GD_CustomItemPools_MainGame.Siren.VladofEpic'
    equip_pool_snipers = 'GD_CustomItemPools_MainGame.Assassin.VladofEpic'
    equip_pool_only_shotguns = 'GD_CustomItemPools_allium.Assassin.AlliumXmasHeads'

    # Shield pool
    pool_shields = 'GD_CustomItemPools_allium.Mechro.AlliumTGHeads'

    ###
    ### Enemy changes
    ###

    enemy_dipl = (
            # ARs
            [
                (0, 'GD_BoneHead_v3.Population.PawnBalance_BoneHead_V3'),
                (0, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BikerBadass'),
                (0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_Hamlock'),
                (0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_JohnnyAbs'),
                (0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_TonyGlutes'),
                (0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_SayFaceTroll'),
                (0, 'GD_Iris_Population_Loader.Balance.Iris_PawnBalance_LoaderBadass'),
                (0, 'GD_Orchid_Pop_Deserters.Deserter1.PawnBalance_Orchid_Deserter1'),
                (0, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderBadass'),
                (0, 'GD_Orchid_Pop_Pervbot.PawnBalance_Orchid_Pervbot'),
                (0, 'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman'),
                (0, 'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman_Solo'),
                (0, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman2'),
                (0, 'GD_Population_Bruiser.Balance.PawnBalance_Bruiser_Muscles'),
                (0, 'GD_Population_Engineer.Balance.Unique.PawnBalance_DJHyperion'),
                (0, 'GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderBadass'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderBadass_HealthCashAmmoOnly'),
                (0, 'GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2'),
                (0, 'GD_Population_Loader.Balance.Unique.PawnBalance_PinocchioBot'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_Ep13_Roland'), # sure, why not?
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_Jimmy'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_CombatEngineer'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Goliath'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderGUN'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderJET'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Marauder'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Nomad'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Rat'),
                (0, 'GD_Population_Nomad.Balance.Unique.PawnBalance_Prospector'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_RatEasterEgg'),
                (0, 'GD_Population_Sheriff.Balance.PawnBalance_Deputy'),
                (0, 'GD_Population_Sheriff.Balance.PawnBalance_Marshal'),
                (0, 'GD_MarauderBadass_Digi.Population.PawnBalance_MarauderBadass_Digi'),
            ],
            # Pistols
            [
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_BrningRedneck'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_JimboRiding'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_Mobley'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_Dan'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_Laney'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_Lee'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_Mick'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_Ralph'),
            ],
            # Shotguns
            [
                (1, 'GD_Assassin2_Digi.Population.PawnBalance_Assassin2_Digi'),
                (0, 'GD_Assassin4_Digi.Population.PawnBalance_Assassin4_Digi'),
                (0, 'GD_ButcherBoss.Balance.PawnBalance_ButcherBoss'),
                (0, 'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman_MarauderMaster'),
                (0, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_TectorHodunk_Combat'),
                (1, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_Jimmy'),
                (1, 'GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4'),
                (0, 'GD_Population_Rat.Balance.Unique.PawnBalance_Mortar'),
                (0, 'GD_Z1_InMemoriamData.Balance.PawnBalance_Boll'),
            ],
            # SMGs
            [
                (0, 'GD_Assassin1_Digi.Population.PawnBalance_Assassin1_Digi'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1'),
                (0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_MickZaford_Combat'),
                (0, 'GD_Population_Midget.Balance.PawnBalance_MidgetBadass'),
            ],
            # All
            [
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_BikeRiderMarauderBadass'),
                (0, 'GD_Iris_Population_BikeRider.Balance.PawnBalance_Iris_RaidBikeMarauderBadass'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderGuard'),
            ],
            # Launchers
            [
                (0, 'GD_Population_Goliath.Balance.Unique.PawnBalance_SmashHead'),
                (0, 'GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike'),
            ],
            # Snipers
            [
            ],
            # Only Shotguns
            [
                (0, 'GD_Population_Engineer.Balance.Unique.PawnBalance_Leprechaun'),
            ],
            # Shields
            [
                (2, 'GD_Z1_InMemoriamData.Balance.PawnBalance_Boll'),
                (2, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BikerBadass'),
                (1, 'GD_Assassin1_Digi.Population.PawnBalance_Assassin1_Digi'),
                (0, 'GD_Assassin2_Digi.Population.PawnBalance_Assassin2_Digi'),
                (0, 'GD_Assassin3_Digi.Population.PawnBalance_Assassin3_Digi'),
                (1, 'GD_Assassin4_Digi.Population.PawnBalance_Assassin4_Digi'),
                (2, 'GD_BoneHead_v3.Population.PawnBalance_BoneHead_V3'),
                (0, 'GD_ButcherBoss2.Balance.PawnBalance_ButcherBoss2'),
                (0, 'GD_ButcherBoss3.Balance.PawnBalance_ButcherBoss3'),
                (0, 'GD_LoaderUltimateBadass_Digi.Population.PawnBalance_LoaderUltimateBadass_Digi'),
                (1, 'GD_MarauderBadass_Digi.Population.PawnBalance_MarauderBadass_Digi'),
                (1, 'GD_MrMercy_Digi.Balance.PawnBalance_MrMercy_Digi'),
                (1, 'GD_Orchid_Pop_Loader.Balance.PawnBalance_OrchidLoaderBadass'),
                (0, 'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_BigSleep'),
                (1, 'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman_Solo'),
                (1, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman'),
                (1, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman2'),
                (1, 'GD_Population_Engineer.Balance.Unique.PawnBalance_DJHyperion'),
                (1, 'GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle'),
                (1, 'GD_Population_Engineer.Balance.Unique.PawnBalance_Leprechaun'),
                (1, 'GD_Population_Goliath.Balance.PawnBalance_GoliathLootGoon'),
                (1, 'GD_Population_Jack.Balance.PawnBalance_JacksBodyDouble'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderBadass'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderBadass_HealthCashAmmoOnly'),
                (1, 'GD_Population_Loader.Balance.PawnBalance_LoaderGuard'),
                (0, 'GD_Population_Loader.Balance.PawnBalance_LoaderSuperBadass'),
                (0, 'GD_Population_Loader.Balance.Unique.PawnBalance_LoaderWAR_1340'),
                (2, 'GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2'), # UCP compat - does not have shields in vanilla
                (1, 'GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1'),
                (2, 'GD_Population_Marauder.Balance.Unique.PawnBalance_MickZaford_Combat'),
                (1, 'GD_Population_Marauder.Balance.Unique.PawnBalance_Mobley'),
                (2, 'GD_Population_Marauder.Balance.Unique.PawnBalance_TectorHodunk_Combat'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_Engineer'),
                (1, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderGUN'),
                (1, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderJET'),
                (0, 'GD_Population_Midget.Balance.LootMidget.PawnBalance_LootMidget_LoaderWAR'),
                (0, 'GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2'),
                (1, 'GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt'),
                (1, 'GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike'),
                (1, 'GD_Population_Nomad.Balance.Unique.PawnBalance_MrMercy'),
                (1, 'GD_Population_Nomad.Balance.Unique.PawnBalance_Prospector'),
                (0, 'GD_Population_Psycho.Balance.Unique.PawnBalance_Assassin3'),
                (0, 'GD_Population_Psycho.Balance.Unique.PawnBalance_IncineratorVanya_Combat'),
                (0, 'GD_Population_Psycho.Balance.Unique.PawnBalance_RakkMan'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_Dan'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_Laney'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_Lee'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_Mick'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_Mortar'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_Ralph'),
                (1, 'GD_Population_Rat.Balance.Unique.PawnBalance_RatEasterEgg'),
                (1, 'GD_Population_Sheriff.Balance.PawnBalance_Deputy'),
                (1, 'GD_Population_Sheriff.Balance.PawnBalance_Sheriff'),
                (0, 'GD_PsychoBadass_Digi.Population.PawnBalance_PsychoBadass_Digi'),

                # Bosses follow - I'm actually not sure if we want to be doing these or not.
                (3, 'GD_Iris_Population_MotorMama.Balance.Iris_PawnBalance_MotorMama'), # Index for Motor Mama shields is 2 in vanilla game
                (1, 'GD_Iris_Population_PyroPete.Balance.Iris_PawnBalance_Pyro_Pete'),
                (0, 'GD_Aster_Pop_Wizards.Balance.PawnBalance_JackWarlock_Demon'),
                (0, 'GD_Aster_Pop_Wizards.Balance.PawnBalance_JackWarlock_DemonFall'),
                (0, 'GD_Aster_Pop_Wizards.Balance.PawnBalance_JackWarlock_MirrorImage'),
                (0, 'GD_Aster_Pop_Wizards.Balance.PawnBalance_JackWarlock_Phase2'),
                (2, 'GD_Iris_Population_PistonBoss.Balance.Iris_PawnBalance_PistonBoss'), # UCP Compat: Shield index is 0 in vanilla
                (0, 'GD_Iris_Population_RaidPete.Balance.Iris_PawnBalance_RaidPete'),
                (0, 'GD_Orchid_Pop_LoaderBoss.Balance.PawnBalance_Orchid_LoaderBoss'),
                (0, 'GD_Population_Jack.Balance.PawnBalance_Jack'),
                (0, 'GD_Population_Loader.Balance.Unique.PawnBalance_LoaderGiant'),
                (0, 'GD_Population_Loader.Balance.Unique.PawnBalance_Willhelm'),
                (0, 'GD_Sage_Raid_BeastMaster.Population.Balance_Sage_Raid_BeastMaster'),
            ],
        )

    enemy_pt_cipl = (
            # ARs
            [
                (0, 0, 'GD_Allium_Badass_SnowMarauder.Balance.PawnBalance_Badass_SnowMarauder'),
                (1, 0, 'GD_Allium_Badass_SnowMarauder.Balance.PawnBalance_Badass_SnowMarauder'),
                (2, 0, 'GD_Allium_Badass_SnowMarauder.Balance.PawnBalance_Badass_SnowMarauder'),
                (0, 0, 'GD_CraterMale.Balance.PawnBalance_CraterMale'),
                (1, 0, 'GD_CraterMale.Balance.PawnBalance_CraterMale'),
                (0, 0, 'GD_EngineerMale.Balance.PawnBalance_EngineerMale'),
                (1, 0, 'GD_EngineerMale.Balance.PawnBalance_EngineerMale'),
                (1, 0, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BikerBadass'),
                (1, 0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_Hamlock'),
                (1, 0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_JohnnyAbs'),
                (1, 0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_TonyGlutes'),
                (1, 0, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_SayFaceTroll'),
                (1, 1, 'GD_Orchid_Pop_Deserters.Deserter1.PawnBalance_Orchid_Deserter1'),
                (0, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateCaptain'),
                (1, 0, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateCaptain'),
                (1, 0, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman'),
                (1, 0, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman2'),
                (0, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderBadass'),
                (1, 0, 'GD_Population_Marauder.Balance.PawnBalance_MarauderBadass'),
                (0, 0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_ShirtlessMan'),
                (1, 0, 'GD_Population_Marauder.Balance.Unique.PawnBalance_ShirtlessMan'),
                (0, 0, 'GD_Population_Nomad.Balance.PawnBalance_Nomad_Ambush'),
                (0, 0, 'GD_Population_Nomad.Balance.PawnBalance_NomadBadass'),
                (1, 0, 'GD_Population_Nomad.Balance.PawnBalance_NomadBadass'),
                (0, 0, 'GD_CraterFemale.Balance.PawnBalance_CraterFemale'),
                (1, 0, 'GD_CraterFemale.Balance.PawnBalance_CraterFemale'),
                (0, 0, 'GD_HodunkBadass.Balance.PawnBalance_HodunkBadass'),
                (1, 0, 'GD_HodunkBadass.Balance.PawnBalance_HodunkBadass'),
                (2, 0, 'GD_HodunkBadass.Balance.PawnBalance_HodunkBadass'),
                (0, 0, 'GD_RaiderFemale.Balance.PawnBalance_RaiderFemale'),
                (0, 0, 'GD_RaiderMale.Balance.PawnBalance_RaiderMale'),
                (0, 0, 'GD_ZafordBadass.Balance.PawnBalance_ZafordBadass'),
                (1, 0, 'GD_ZafordBadass.Balance.PawnBalance_ZafordBadass'),
                (2, 0, 'GD_ZafordBadass.Balance.PawnBalance_ZafordBadass'),
            ],
            # Pistols
            [
                (0, 0, 'GD_Lynchwood_Male.Balance.PawnBalance_Lynchwood_Male'),
                (1, 0, 'GD_Lynchwood_Male.Balance.PawnBalance_Lynchwood_Male'),
            ],
            # Shotguns
            [
                (0, 0, 'GD_Population_Nomad.Balance.PawnBalance_BadMaw'),
                (1, 0, 'GD_Population_Nomad.Balance.PawnBalance_BadMaw'),
            ],
            # SMGs
            [
                (0, 0, 'GD_Sage_Pop_DrNakayama.Balance.PawnBalance_Sage_DrNakayama'), # he needs all the help he can get
            ],
            # All
            [
            ],
            # Launchers
            [
            ],
            # Snipers
            [
                (0, 0, 'GD_Lynchwood_Female.Balance.PawnBalance_Lynchwood_Female'),
                (1, 0, 'GD_Lynchwood_Female.Balance.PawnBalance_Lynchwood_Female'),
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
                (0, 1, 'GD_HodunkBadass.Balance.PawnBalance_HodunkBadass'),
                (1, 1, 'GD_HodunkBadass.Balance.PawnBalance_HodunkBadass'),
                (2, 1, 'GD_HodunkBadass.Balance.PawnBalance_HodunkBadass'),
                (1, 1, 'GD_Iris_Population_Biker.Balance.Iris_PawnBalance_BikerBadass'),
                (1, 1, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_Hamlock'),
                (1, 1, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_JohnnyAbs'),
                (1, 1, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_BB_TonyGlutes'),
                (1, 1, 'GD_Iris_Population_Biker.Balance.Unique.Iris_PawnBalance_SayFaceTroll'),
                (0, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderBadass'),
                (1, 1, 'GD_Population_Marauder.Balance.PawnBalance_MarauderBadass'),
                (0, 0, 'GD_Population_Psycho.Balance.Unique.PawnBalance_SavageLee'),
                (1, 0, 'GD_Population_Psycho.Balance.Unique.PawnBalance_SavageLee'),
                (0, 0, 'GD_SandFemale.Balance.PawnBalance_SandFemale'),
                (0, 1, 'GD_ZafordBadass.Balance.PawnBalance_ZafordBadass'),
                (1, 1, 'GD_ZafordBadass.Balance.PawnBalance_ZafordBadass'),
                (2, 1, 'GD_ZafordBadass.Balance.PawnBalance_ZafordBadass'),
                (0, 1, 'GD_Allium_Badass_SnowMarauder.Balance.PawnBalance_Badass_SnowMarauder'),
                (1, 1, 'GD_Allium_Badass_SnowMarauder.Balance.PawnBalance_Badass_SnowMarauder'),
                (2, 1, 'GD_Allium_Badass_SnowMarauder.Balance.PawnBalance_Badass_SnowMarauder'),
                (1, 1, 'GD_CraterFemale.Balance.PawnBalance_CraterFemale'),
                (1, 1, 'GD_CraterMale.Balance.PawnBalance_CraterMale'),
                (0, 1, 'GD_EngineeFemale.Balance.PawnBalance_EngineerFemale'),
                (1, 1, 'GD_EngineeFemale.Balance.PawnBalance_EngineerFemale'),
                (0, 1, 'GD_EngineerMale.Balance.PawnBalance_EngineerMale'),
                (1, 1, 'GD_EngineerMale.Balance.PawnBalance_EngineerMale'),
                (1, 0, 'GD_FleshripperFemale.Balance.PawnBalance_FleshripperFemale'),
                (1, 0, 'GD_FleshripperMale.Balance.PawnBalance_FleshripperMale'),
                (0, 0, 'GD_GoliathGroom.Population.PawnBalance_GoliathGroom'),
                (0, 0, 'GD_GoliathGroom.Population.PawnBalance_GoliathGroomRaid'),
                (1, 0, 'GD_IncineratorFemale.Balance.PawnBalance_IncineratorFemale'),
                (1, 0, 'GD_IncineratorMale.Balance.PawnBalance_IncineratorMale'),
                (1, 1, 'GD_Lynchwood_Female.Balance.PawnBalance_Lynchwood_Female'),
                (1, 1, 'GD_Lynchwood_Male.Balance.PawnBalance_Lynchwood_Male'),
                (1, 0, 'GD_Orchid_Pop_Deserters.Deserter1.PawnBalance_Orchid_Deserter1'),
                (1, 0, 'GD_Orchid_Pop_Deserters.Deserter2.PawnBalance_Orchid_Deserter2'),
                (0, 1, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateCaptain'),
                (1, 1, 'GD_Orchid_Pop_Pirates.Balance.PawnBalance_Orchid_PirateCaptain'),
                (1, 2, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman'), # technically this fixes a bug!
                (1, 2, 'GD_Orchid_Pop_ScarlettCrew.Balance.PawnBalance_Orchid_PirateHenchman2'), # this also fixes a bug!
                (0, 0, 'GD_Population_Constructor.Balance.PawnBalance_ConstructorBadass'),
                (1, 0, 'GD_Population_Constructor.Balance.PawnBalance_ConstructorBadass'),
                (0, 1, 'GD_Population_Marauder.Balance.Unique.PawnBalance_ShirtlessMan'),
                (1, 1, 'GD_Population_Marauder.Balance.Unique.PawnBalance_ShirtlessMan'),
                (1, 0, 'GD_Population_Midget.Balance.Unique.PawnBalance_Midge'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_BadMaw'),
                (1, 1, 'GD_Population_Nomad.Balance.PawnBalance_BadMaw'),
                (0, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadBadass'),
                (1, 1, 'GD_Population_Nomad.Balance.PawnBalance_NomadBadass'),
                (1, 0, 'GD_Population_Psycho.Balance.PawnBalance_PsychoBadass'),
                (1, 0, 'GD_Population_Psycho.Balance.Unique.PawnBalance_ProspectorPsycho'),
                (0, 1, 'GD_RaiderFemale.Balance.PawnBalance_RaiderFemale'),
                (0, 1, 'GD_RaiderMale.Balance.PawnBalance_RaiderMale'),
                (0, 1, 'GD_Sage_Pop_DrNakayama.Balance.PawnBalance_Sage_DrNakayama'), # again, let's give him all the help we can
                (0, 0, 'GD_SandMale.Balance.PawnBalance_SandMale'),
            ],
        )

    enemy_level_ipl = (
            # ARs
            [
                ('Ash_P', 8, 'Ash_P.TheWorld:PersistentLevel.WillowAIPawn_3'),
                ('Ash_P', 8, 'Ash_P.TheWorld:PersistentLevel.WillowAIPawn_47'),
                ('Damtop_P', 12, 'damtop_p.TheWorld:PersistentLevel.WillowAIPawn_20'),
                ('Grass_Lynchwood_P', 8, 'Grass_Lynchwood_P.TheWorld:PersistentLevel.WillowAIPawn_0'),
                ('Grass_Lynchwood_P', 8, 'Grass_Lynchwood_P.TheWorld:PersistentLevel.WillowAIPawn_2'),
                ('Grass_Lynchwood_P', 8, 'Grass_Lynchwood_P.TheWorld:PersistentLevel.WillowAIPawn_86'),
                ('Grass_Lynchwood_P', 8, 'Grass_Lynchwood_P.TheWorld:PersistentLevel.WillowAIPawn_87'),
                ('Grass_Lynchwood_P', 8, 'Grass_Lynchwood_P.TheWorld:PersistentLevel.WillowAIPawn_89'),
                ('Grass_Lynchwood_P', 8, 'Grass_Lynchwood_P.TheWorld:PersistentLevel.WillowAIPawn_90'),
                ('icecanyon_p', 8, 'icecanyon_p.TheWorld:PersistentLevel.WillowAIPawn_69'),
                ('icecanyon_p', 8, 'icecanyon_p.TheWorld:PersistentLevel.WillowAIPawn_70'),
            ],
            # Pistols
            [
            ],
            # Shotguns
            [
                ('Grass_Lynchwood_P', 8, 'Grass_Lynchwood_P.TheWorld:PersistentLevel.WillowAIPawn_91'),
            ],
            # SMGs
            [
            ],
            # All
            [
            ],
            # Launchers
            [
            ],
            # Snipers
            [
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
                ('damtop_p', 13, 'damtop_p.TheWorld:PersistentLevel.WillowAIPawn_20'),
                ('Fridge_P', 12, 'Fridge_P.TheWorld:PersistentLevel.WillowAIPawn_228'),
            ],
        )

    enemy_dl_ia = (
            # ARs
            [
            ],
            # Pistols
            [
            ],
            # Shotguns
            [
            ],
            # SMGs
            [
            ],
            # All
            [
            ],
            # Launchers
            [
            ],
            # Snipers
            [
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
            ],
        )

    enemy_nipl = (
            # ARs
            [
            ],
            # Pistols
            [
            ],
            # Shotguns
            [
                (0, 'GD_Nast_Native_Soldier.Anims.Anim_Soldier_Warcry:BehaviorProviderDefinition_0.Behavior_AIChangeInventory_3'),
                (0, 'GD_Native_Soldier.Anims.Anim_Soldier_Warcry:BehaviorProviderDefinition_0.Behavior_AIChangeInventory_211'),
            ],
            # SMGs
            [
                (0, 'GD_Nast_Native_Soldier.Anims.Anim_Soldier_Warcry:BehaviorProviderDefinition_0.Behavior_AIChangeInventory_2'),
                (0, 'GD_Native_Soldier.Anims.Anim_Soldier_Warcry:BehaviorProviderDefinition_0.Behavior_AIChangeInventory_212'),
            ],
            # All
            [
                (0, 'GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBikerBadass_Angels:PopulationFactoryBalancedAIPawn_1.Behavior_AIChangeInventory_5'),
                (0, 'GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBikerBadass_Dragon:PopulationFactoryBalancedAIPawn_1.Behavior_AIChangeInventory_2'),
                (0, 'GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBikerBadass_Torgue:PopulationFactoryBalancedAIPawn_1.Behavior_AIChangeInventory_2'),
                (0, 'GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerBadass_Angels:PopulationFactoryBalancedAIPawn_1.Behavior_AIChangeInventory_5'),
                (0, 'GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerBadass_Dragon:PopulationFactoryBalancedAIPawn_1.Behavior_AIChangeInventory_2'),
                (0, 'GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerBadass_Torgue:PopulationFactoryBalancedAIPawn_1.Behavior_AIChangeInventory_2'),
            ],
            # Launchers
            [
            ],
            # Snipers
            [
            ],
            # Only Shotguns
            [
            ],
            # Shields
            [
            ],
        )

###
### Convenience functions
###

def get_balanced_items(items):
    """
    Returns a string containing a BalancedItems array with the given `items`.
    Each element of the list `items` should be a tuple, the first element
    being the itempool class name, the second being the weight of that
    item, and the third (optional) being an `invbalance` (or None).  If `None`,
    the item will be put into the ItmPoolDefinition attribute - otherwise it
    will be put into the InvBalanceDefinition attribute, with the given
    `invbalance` string as the type of object being linked to (most commonly
    either WeaponBalanceDefinition or InventoryBalanceDefinition)
    """
    bal_items = []
    new_items = []
    for item in items:
        if len(item) == 2:
            new_items.append((item[0], item[1], None))
        else:
            new_items.append((item[0], item[1], item[2]))
    for (classname, weight, invbalance) in new_items:
        if classname:
            if invbalance:
                itmpool = 'None'
                invbal = "{}'{}'".format(invbalance, classname)
            else:
                itmpool = "ItemPoolDefinition'{}'".format(classname)
                invbal = 'None'
        else:
            itmpool = 'None'
            invbal = 'None'
        bal_items.append("""
            (
                ItmPoolDefinition={},
                InvBalanceDefinition={},
                Probability=(
                    BaseValueConstant={},
                    BaseValueAttribute=None,
                    InitializationDefinition=None,
                    BaseValueScaleConstant=1
                ),
                bDropOnDeath=True
            )
            """.format(itmpool, invbal, weight))
    return '({})'.format(','.join(bal_items))

def get_balanced_set(objectname, items):
    """
    Returns a regular "set" command to set `objectname`'s BalancedItems
    attribute to an array with the specified `items`.  The bulk of the
    work here is done in `get_balanced_items()`.
    """
    return "set {} BalancedItems\n{}".format(objectname,
            get_balanced_items(items))

def disable_balanced_drop(prefix, pool, item_num):
    """
    Disables an item in a pool's BalancedItems array.  Rather than actually
    disabling or deleting, we're going to redirect to the locker items pool,
    so that the other drop weights in the pool aren't changed.  The player
    will just see slightly more ammo/health/eridium instead.  Returns a list
    of XMLish strings to add to the mod file.
    """
    global hfs
    to_pool = 'GD_Itempools.LootablePools.Pool_Locker_Items_CashAndAmmo'
    hotfix_id_itmpool = 'disable_balanced_itmpool_{}'.format(hfs.num_hotfixes())
    hotfix_id_invbal = 'disable_balanced_invbal_{}'.format(hfs.num_hotfixes())
    hfs.add_level_hotfix(hotfix_id_itmpool,
        'DisableBalanced',
        ",{},BalancedItems[{}].ItmPoolDefinition,,ItemPoolDefinition'{}'".format(
            pool, item_num, to_pool))
    hfs.add_level_hotfix(hotfix_id_invbal,
        'DisableBalanced',
        ',{},BalancedItems[{}].InvBalanceDefinition,,None'.format(
            pool, item_num))
    return [
            '{}{}'.format(prefix, hfs.get_hotfix(hotfix_id_itmpool).get_xml()),
            '{}{}'.format(prefix, hfs.get_hotfix(hotfix_id_invbal).get_xml()),
        ]

def set_dipl_item_pool(hotfix_name, classname, index, pool,
        level=None, activated=True):
    """
    Sets an entire DefaultItemPoolList entry on the given `classname`, at
    the given `index`, to point towards the pool `pool`.  Will be done with
    a hotfix with the ID `hotfix_name`, optionally in the level `level`.
    To disable (for inclusion into a MUT category, for instance), pass
    `activated`=`False`.
    """
    if level is None:
        level = ''
    hfs.add_level_hotfix(hotfix_name, 'DIPLItemPool',
        """{},{},DefaultItemPoolList[{}],,
        (
            ItemPool=ItemPoolDefinition'{}',
            PoolProbability=(
                BaseValueConstant=1,
                BaseValueAttribute=None,
                InitializationDefinition=None,
                BaseValueScaleConstant=1
            )
        )""".format(level, classname, index, pool),
        activated=activated)

def set_pt_cipl_item_pool(hotfix_name, classname, pt_index, cipl_index,
        pool, level=None, activated=True):
    """
    Sets an entire PlayThroughs[x].CustomItemPoolList entry on the given
    `classname`, at the given playthrough index `pt_index` and CIPL index
    `cipl_index`, to point towards the pool `pool`.  Will be done with
    a hotfix with the ID `hotfix_name`, optionally in the level `level`.
    To disable (for inclusion into a MUT category, for instance), pass
    `activated`=`False`.
    """
    if level is None:
        level = ''
    hfs.add_level_hotfix(hotfix_name, 'PTCIPLItemPool',
        """{},{},PlayThroughs[{}].CustomItemPoolList[{}],,
        (
            ItemPool=ItemPoolDefinition'{}',
            PoolProbability=(
                BaseValueConstant=1,
                BaseValueAttribute=None,
                InitializationDefinition=None,
                BaseValueScaleConstant=1
            )
        )""".format(level, classname, pt_index, cipl_index, pool),
        activated=activated)

def set_generic_item_prob(hotfix_name, classname, attribute,
        level=None, prob=None, activated=True):
    """
    Sets a probability in the given `classname`, on the attribute `attribute`.
    Will do so via a hotfix with the name `hotfix_name`.  If `prob` is not
    specified, the item will be disabled (ie: given a zero probability).
    Otherwise, pass `1` for the prob (or any other percentage you want).
    To disable the hotfix by default (for inclusion in a MUT, for instance),
    pass `activated`=`False`.
    """
    global hfs
    if level is None:
        level = ''
    if prob is None:
        prob = 0
    hfs.add_level_hotfix(hotfix_name, 'Disable',
        """{},{},{},,
        (
            BaseValueConstant={},
            BaseValueAttribute=None,
            InitializationDefinition=None,
            BaseValueScaleConstant=1
        )""".format(level, classname, attribute, prob),
        activated=activated)

def set_bi_item_pool(hotfix_name, classname, index, item,
        level=None, prob=None, activated=True, invbalance=None):
    """
    Sets an entire BalancedItem structure
    """
    global hfs
    if level is None:
        level = ''
    if prob is None:
        prob = 1
    if invbalance:
        itmpool = 'None'
        invbal = "{}'{}'".format(invbalance, item)
    else:
        itmpool = "ItemPoolDefinition'{}'".format(item)
        invbal = 'None'
    hfs.add_level_hotfix(hotfix_name, 'SetBIItem',
        """{},{},BalancedItems[{}],,
        (
            ItmPoolDefinition={},
            InvBalanceDefinition={},
            Probability=(
                BaseValueConstant={},
                BaseValueAttribute=None,
                InitializationDefinition=None,
                BaseValueScaleConstant=1
            ),
            bDropOnDeath=True
        )""".format(level, classname, index, itmpool, invbal, prob),
        activated=activated)

def set_bi_item_prob(hotfix_name, classname, index, level=None,
        prob=None, activated=True):
    """
    Sets a BalancedItems probability.
    """
    set_generic_item_prob(hotfix_name, classname,
        'BalancedItems[{}].Probability'.format(index),
        level=level,
        prob=prob,
        activated=activated)

def set_dipl_item_prob(hotfix_name, classname, index, level=None,
        prob=None, activated=True):
    """
    Sets a DefaultItemPoolList probability.
    """
    set_generic_item_prob(hotfix_name, classname,
        'DefaultItemPoolList[{}].PoolProbability'.format(index),
        level=level,
        prob=prob,
        activated=activated)

def set_pt_cipl_item_prob(hotfix_name, classname,
        pt_index, poollist_index, level=None, prob=None, activated=True):
    """
    Sets a PlayThroughs[x].CustomItemPoolList probability in the given
    `classname`, at the playthrough index `pt_index` and CustomItemPoolList
    index `poollist_index`.
    """
    set_generic_item_prob(hotfix_name, classname,
        'PlayThroughs[{}].CustomItemPoolList[{}].PoolProbability'.format(
            pt_index, poollist_index),
        level=level,
        prob=prob,
        activated=activated)

def setup_boss_pool(hotfix_id, level, pool, default_gear, unique_gear, activated=True):
    """
    Sets up our specified `pool` using the given `hotfix_id`, active in the
    level `level`.  The "default" ItemPool which the boss ordinarily draws from
    is specified by `default_gear`, and the pool's unique gear in a list of
    `unique_gear`, each element of which should be a tuple with three elements:
        1) The unique pool to drop from / gear to drop.
        2) The percent chance of dropping this pool/gear
        3) If this is an item, the InvBalanceDefinition type of the item.
    If the total of all the percent chances in `unique_gear` is greater than
    1, the `default_gear` will never actually be dropped.  To disable this
    hotfix (for inclusion in a MUT, for instance) pass `activated`=`False`.
    """
    global hfs
    total_unique = 0
    bal_items_tuples = []
    for (unique, pct, baldef) in unique_gear:
        total_unique += pct
        bal_items_tuples.append((unique, pct, baldef))
    if default_gear and total_unique < 1:
        bal_items_tuples.append((default_gear, round(1 - total_unique, 6), None))
    hfs.add_level_hotfix(hotfix_id, 'BossPool',
        '{},{},BalancedItems,,{}'.format(
            level,
            pool,
            get_balanced_items(bal_items_tuples)),
        activated=activated)

###
### Code to generate the mod
###

hfs = Hotfixes()
regular = Regular(hfs)
badass = Badass(hfs)
other = OtherConfig()

# Get rid of global world drops.
prefix = ' '*(4*3)
drop_disables = []
for (pool, index) in [
        ('GD_Itempools.GeneralItemPools.Pool_Gear', 0),
        ('GD_Itempools.GeneralItemPools.Pool_GunsAndGear', 0),
        ('GD_Itempools.GeneralItemPools.Pool_GunsAndGearDropNumPlayersPlusOne', 0),
        ('GD_Itempools.GeneralItemPools.Pool_GunsAndGear', 1),
        ('GD_Itempools.GeneralItemPools.Pool_GunsAndGearDropNumPlayersPlusOne', 1),
        ('GD_Itempools.GeneralItemPools.Pool_Items_Small', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_01_Common', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_01_Common', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_02_Uncommon', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_02_Uncommon', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_02_UncommonsRaid', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_02_UncommonsRaid', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_04_Rare', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_04_Rare', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_04_RaresRaid', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_04_RaresRaid', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_05_VeryRare', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_05_VeryRare', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_06_Legendary', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_06_Legendary', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedLaunchers', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedLaunchers', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedLaunchers', 2),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedPistols', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedPistols', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedPistols', 2),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedRifles', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedRifles', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedRifles', 2),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedShotguns', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedShotguns', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedShotguns', 2),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedSMGs', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedSMGs', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedSMGs', 2),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedSniper', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedSniper', 1),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedSniper', 2),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedShields', 0),
        ('GD_Itempools.EnemyDropPools.Pool_GunsAndGear_WeightedShields', 1),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Weapons_GunsAndGear', 1),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Weapons_GunsAndGear', 2),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Weapons_GunsAndGear', 3),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Weapons_GunsAndGear', 4),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Items', 0),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Items', 1),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Items', 2),
        ('GD_Itempools.Treasure_ChestPools.Pool_EpicChest_Items', 3),
        ('GD_Itempools.Treasure_ChestPools.Pool_WeaponChest_Items', 0),
        ('GD_Itempools.Treasure_ChestPools.Pool_WeaponChest_Items', 1),
        ('GD_Itempools.Treasure_ChestPools.Pool_WeaponChest_Items', 2),
        ('GD_Itempools.Treasure_ChestPools.Pool_WeaponChest_Items', 3),
        # BL2 Better Loot would require clearing out index 4 of Pool_WeaponChest_Items, too.
        ('GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol', 0),
        ('GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol_P2_P3', 0),
        ('GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol_P4', 0),
        ]:
    drop_disables.extend(disable_balanced_drop(prefix, pool, index))
other.disable_world_sets = "\n\n".join(drop_disables)

# Configure rarity pools
rarity_sections = {}
line_prefix = ''
line_suffix = ''
hotfix_activated = True
for (rarity_key, rarity_label) in DropConfig.rarity_presets:

    for config in [regular, badass]:

        config.set_rarity_weights(rarity_key)

        config.set_rarity_ar = get_balanced_set(
            config.rarity_pool_ar,
            [
                ('GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common', config.weight_common),
                ('GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon', config.weight_uncommon),
                ('GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare', config.weight_rare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare', config.weight_veryrare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien', config.weight_alien),
                ('GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary', config.weight_legendary),
            ])

        config.set_rarity_launchers = get_balanced_set(
            config.rarity_pool_launchers,
            [
                ('GD_Itempools.WeaponPools.Pool_Weapons_Launchers_01_Common', config.weight_common),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Launchers_02_Uncommon', config.weight_uncommon),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Launchers_04_Rare', config.weight_rare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare', config.weight_veryrare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare_Alien', config.weight_alien),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary', config.weight_legendary),
            ])

        config.set_rarity_pistols = get_balanced_set(
            config.rarity_pool_pistols,
            [
                ('GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common', config.weight_common),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon', config.weight_uncommon),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare', config.weight_rare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare', config.weight_veryrare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien', config.weight_alien),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary', config.weight_legendary),
            ])

        config.set_rarity_smg = get_balanced_set(
            config.rarity_pool_smg,
            [
                ('GD_Itempools.WeaponPools.Pool_Weapons_SMG_01_Common', config.weight_common),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SMG_02_Uncommon', config.weight_uncommon),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SMG_04_Rare', config.weight_rare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare', config.weight_veryrare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare_Alien', config.weight_alien),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary', config.weight_legendary),
            ])

        config.set_rarity_shotguns = get_balanced_set(
            config.rarity_pool_shotguns,
            [
                ('GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common', config.weight_common),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon', config.weight_uncommon),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare', config.weight_rare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare', config.weight_veryrare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien', config.weight_alien),
                ('GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary', config.weight_legendary),
            ])

        config.set_rarity_snipers = get_balanced_set(
            config.rarity_pool_snipers,
            [
                ('GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_01_Common', config.weight_common),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_02_Uncommon', config.weight_uncommon),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare', config.weight_rare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare', config.weight_veryrare),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare_Alien', config.weight_alien),
                ('GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary', config.weight_legendary),
            ])

        # Shield pool (rarity + equip in one, since we don't need to make two choices)

        config.set_shields = get_balanced_set(
            config.pool_shields,
            [
                ('GD_Itempools.ShieldPools.Pool_Shields_All_01_Common', config.weight_common),
                ('GD_Itempools.ShieldPools.Pool_Shields_All_02_Uncommon', config.weight_uncommon),
                ('GD_Itempools.ShieldPools.Pool_Shields_All_04_Rare', config.weight_rare),
                ('GD_Itempools.ShieldPools.Pool_Shields_All_05_VeryRare', config.weight_veryrare),
                ('GD_Itempools.ShieldPools.Pool_Shields_All_06_Legendary', config.weight_legendary),
            ])

    # Set up Jack's Body Double's equip pool
    body_double_key = '{}_body_double_equip'.format(rarity_key)
    hfs.add_level_hotfix(body_double_key, 'BodyDouble',
        """HyperionCity_P,
        GD_JacksBodyDouble.WeaponPools.Pool_Weapons_JackBodyDouble_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Weap_SMG.A_Weapons.SMG_Hyperion', badass.weight_common, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons.SMG_Hyperion_2_Uncommon', badass.weight_uncommon, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons.SMG_Hyperion_3_Rare', badass.weight_rare, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons.SMG_Hyperion_4_VeryRare', badass.weight_veryrare, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons.SMG_Hyperion_5_Alien', badass.weight_alien, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons_Legendary.SMG_Hyperion_5_Bitch', badass.weight_legendary, 'WeaponBalanceDefinition'),
            ])),
            activated=hotfix_activated)

    # Torgue DLC equip rarities (only regular)

    torguehfs = Hotfixes(nameprefix='{}TorgueRarity'.format(rarity_key))

    torguehfs.add_level_hotfix('angel_pistols', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_Pistols_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Pistols_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Pistols_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Pistols_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Pistols_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Pistols_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Pistols_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('angel_shotguns', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_Shotguns_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Shotguns_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Shotguns_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Shotguns_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Shotguns_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Shotguns_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_Shotguns_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('angel_smg', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_SMG_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SMG_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SMG_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SMG_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SMG_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SMG_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SMG_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('angel_snipers', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('dragon_pistols', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_DragonGang_Pistols_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_Pistols_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_Pistols_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_Pistols_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_Pistols_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_Pistols_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_Pistols_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('dragon_smg', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_DragonGang_SMG_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SMG_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SMG_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SMG_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SMG_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SMG_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SMG_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('dragon_snipers', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('torgue_pistols', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_TorgueGang_Pistols_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Pistols_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Pistols_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Pistols_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Pistols_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Pistols_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Pistols_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('torgue_shotguns', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    torguehfs.add_level_hotfix('torgue_ar', 'Equip',
        """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_TorgueGang_AR_EnemyUse,
        BalancedItems,,{}""".format(get_balanced_items(
            [
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_AR_01_Common', regular.weight_common),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_AR_02_Uncommon', regular.weight_uncommon),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_AR_04_Rare', regular.weight_rare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_AR_05_VeryRare', regular.weight_veryrare),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_AR_05_VeryRare_Alien', regular.weight_alien),
                ('GD_Iris_ItemPools.WeaponPools.Pool_Weapons_TorgueGang_AR_06_Legendary', regular.weight_legendary),
            ])),
            activated=hotfix_activated)

    with open('input-file-rarity.txt', 'r') as df:
        rarity_sections[rarity_key] = df.read().format(
                section_label=rarity_label,
                line_prefix=line_prefix,
                line_suffix=line_suffix,
                regular=regular,
                badass=badass,
                body_double_equip_hotfix_string=hfs.get_hotfix(body_double_key).get_xml(),
                torguehotfixes=torguehfs,
                )

    line_prefix = '#'
    line_suffix = '<off>'
    hotfix_activated = False

# Configure the gun type probabilities
for config in [regular, badass]:

    # Configure Equip pools

    config.set_equip_all = get_balanced_set(
        config.equip_pool_all,
        [
            (config.rarity_pool_pistols, config.drop_prob_pistols),
            (config.rarity_pool_ar, config.drop_prob_ar),
            (config.rarity_pool_smg, config.drop_prob_smg),
            (config.rarity_pool_shotguns, config.drop_prob_shotguns),
            (config.rarity_pool_snipers, config.drop_prob_snipers),
            (config.rarity_pool_launchers, config.drop_prob_launchers),
        ])

    config.set_equip_ar = get_balanced_set(
        config.equip_pool_ar,
        [
            (config.rarity_pool_pistols, config.drop_prob_pistols),
            (config.rarity_pool_ar, config.drop_prob_ar*config.weight_scale),
            (config.rarity_pool_smg, config.drop_prob_smg),
            (config.rarity_pool_shotguns, config.drop_prob_shotguns),
            (config.rarity_pool_snipers, config.drop_prob_snipers),
            (config.rarity_pool_launchers, config.drop_prob_launchers),
        ])

    config.set_equip_pistols = get_balanced_set(
        config.equip_pool_pistols,
        [
            (config.rarity_pool_pistols, config.drop_prob_pistols*config.weight_scale),
            (config.rarity_pool_ar, config.drop_prob_ar),
            (config.rarity_pool_smg, config.drop_prob_smg),
            (config.rarity_pool_shotguns, config.drop_prob_shotguns),
            (config.rarity_pool_snipers, config.drop_prob_snipers),
            (config.rarity_pool_launchers, config.drop_prob_launchers),
        ])

    config.set_equip_shotguns = get_balanced_set(
        config.equip_pool_shotguns,
        [
            (config.rarity_pool_pistols, config.drop_prob_pistols),
            (config.rarity_pool_ar, config.drop_prob_ar),
            (config.rarity_pool_smg, config.drop_prob_smg),
            (config.rarity_pool_shotguns, config.drop_prob_shotguns*config.weight_scale),
            (config.rarity_pool_snipers, config.drop_prob_snipers),
            (config.rarity_pool_launchers, config.drop_prob_launchers),
        ])

    config.set_equip_smg = get_balanced_set(
        config.equip_pool_smg,
        [
            (config.rarity_pool_pistols, config.drop_prob_pistols),
            (config.rarity_pool_ar, config.drop_prob_ar),
            (config.rarity_pool_smg, config.drop_prob_smg*config.weight_scale),
            (config.rarity_pool_shotguns, config.drop_prob_shotguns),
            (config.rarity_pool_snipers, config.drop_prob_snipers),
            (config.rarity_pool_launchers, config.drop_prob_launchers),
        ])

    config.set_equip_launchers = get_balanced_set(
        config.equip_pool_launchers,
        [
            (config.rarity_pool_launchers, 1),
        ])

    config.set_equip_snipers = get_balanced_set(
        config.equip_pool_snipers,
        [
            (config.rarity_pool_snipers, 1),
        ])

    config.set_equip_only_shotguns = get_balanced_set(
        config.equip_pool_only_shotguns,
        [
            (config.rarity_pool_shotguns, 1),
        ])

# Make Torgue DLC equip pools drop on death.
hfs.add_level_hotfix('torgue_angel_equip', 'TorgueEquip',
    """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_AngelGang_All_ButLaunchers_Use,
    BalancedItems,,{}""".format(get_balanced_items([
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_Pistols_EnemyUse', regular.drop_prob_pistols, None),
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_Shotguns_EnemyUse', regular.drop_prob_shotguns, None),
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_SMG_EnemyUse', regular.drop_prob_smg, None),
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_AngelGang_SniperRifles_EnemyUse', regular.drop_prob_snipers, None),
        (regular.rarity_pool_launchers, regular.drop_prob_launchers, None),
    ])))

hfs.add_level_hotfix('torgue_dragon_equip', 'TorgueEquip',
    """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_DragonGang_All_ButLaunchers_Use,
    BalancedItems,,{}""".format(get_balanced_items([
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_DragonGang_Pistols_EnemyUse', regular.drop_prob_pistols, None),
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_DragonGang_SMG_EnemyUse', regular.drop_prob_smg, None),
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_DragonGang_SniperRifles_EnemyUse', regular.drop_prob_snipers, None),
        (regular.rarity_pool_launchers, regular.drop_prob_launchers, None),
    ])))

hfs.add_level_hotfix('torgue_torgue_equip', 'TorgueEquip',
    """,GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_TorgueGangWeapons_All_ButLaunchers_Use,
    BalancedItems,,{}""".format(get_balanced_items([
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_TorgueGang_Pistols_EnemyUse', regular.drop_prob_pistols, None),
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_TorgueGang_AR_EnemyUse', regular.drop_prob_ar, None),
        ('GD_Iris_ItemPoolsEnemyUse.WeaponPools.Pool_Weapons_TorgueGang_Shotguns_EnemyUse', regular.drop_prob_shotguns, None),
        (regular.rarity_pool_launchers, regular.drop_prob_launchers, None),
    ])))

# Improve "medical mystery" pool (used in a couple of places, actually)
hfs.add_level_hotfix('medicalmystery', 'MedicalMystery',
    """,GD_ItempoolsEnemyUse.Turrets.MedicalMystery_AlienGun,
    BalancedItems,,{}""".format(get_balanced_items([
        ('GD_Weap_AssaultRifle.A_Weapons.AR_Bandit_5_Alien', 1, 'WeaponBalanceDefinition'),
    ])))

# Laney's Dwarves - Better Loot Compat.  Deactivate the extra gemstone drop.

for idx in range(7):
    set_dipl_item_prob('laney_dwarf_pool_{}'.format(idx),
        'GD_Population_Midget.Balance.Unique.PawnBalance_LaneyDwarf{}'.format(idx+1),
        3,
        level='Fridge_P')

# Legendary Pool management
unique_hotfixes = []
pearl_hotfixes = []
seraph_hotfixes = []
for (guntype, legendaries, uniques, pearls, seraphs) in [
        (
            'AssaultRifles',
            [
                # Regular Legendaries
                'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Bandit_5_Madhouse',
                'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Dahl_5_Veruc',
                'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Jakobs_5_HammerBuster',
                'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Torgue_5_KerBlaster',
                'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Vladof_5_Sherdifier',
            ],
            [
                # Uniques
                'GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre',
                'GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy',
                'GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten',
                'GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot',
                'GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier',
                'GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper',
                'GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy',
                'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_3_Scorpio',
                'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper',
                'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher',
                'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail',
            ],
            [
                # Pearls
                'GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar',
                'GD_Gladiolus_Weapons.AssaultRifle.AR_Dahl_6_Bearcat',
                'GD_Lobelia_Weapons.AssaultRifles.AR_Jakobs_6_Bekah',
            ],
            [
                # Seraphs
                'GD_Aster_RaidWeapons.AssaultRifles.Aster_Seraph_Seeker_Balance',
                'GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance',
                'GD_Sage_RaidWeapons.AssaultRifle.Sage_Seraph_LeadStorm_Balance',
            ],
        ),
        (
            'Launchers',
            [
                # Regular Legendaries
                'GD_Weap_Launchers.A_Weapons_Legendary.RL_Bandit_5_BadaBoom',
                'GD_Weap_Launchers.A_Weapons_Legendary.RL_Maliwan_5_Pyrophobia',
                'GD_Weap_Launchers.A_Weapons_Legendary.RL_Tediore_5_Bunny',
                'GD_Weap_Launchers.A_Weapons_Legendary.RL_Torgue_5_Nukem',
                'GD_Weap_Launchers.A_Weapons_Legendary.RL_Vladof_5_Mongol',
                'GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet',
            ],
            [
                # Uniques
                'GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive',
                'GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder',
                'GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer',
                'GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster',
            ],
            [
                # Pearls
                'GD_Gladiolus_Weapons.Launchers.RL_Torgue_6_Tunguska',
            ],
            [
                # Seraphs
                'GD_Orchid_RaidWeapons.RPG.Ahab.Orchid_Seraph_Ahab_Balance',
            ],
        ),
        (
            'Pistols',
            [
                # Regular Legendaries
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Bandit_5_Gub',
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Tediore_5_Gunerang',
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Dahl_5_Hornet',
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Vladof_5_Infinity',
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Torgue_5_Calla',
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Maliwan_5_ThunderballFists',
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Jakobs_5_Maggie',
                'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Hyperion_5_LogansGun',
            ],
            [
                # Uniques
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge',
                'GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle',
                'GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator',
                'GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket',
                'GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law',
                'GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas',
                'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox',
            ],
            [
                # Pearls
                'GD_Gladiolus_Weapons.Pistol.Pistol_Jakobs_6_Unforgiven',
                'GD_Gladiolus_Weapons.Pistol.Pistol_Vladof_6_Stalker',
                'GD_Lobelia_Weapons.Pistol.Pistol_Maliwan_6_Wanderlust',
            ],
            [
                # Seraphs
                'GD_Orchid_RaidWeapons.Pistol.Devastator.Orchid_Seraph_Devastator_Balance',
                'GD_Sage_RaidWeapons.Pistol.Sage_Seraph_Infection_Balance',
                'GD_Aster_RaidWeapons.Pistols.Aster_Seraph_Stinger_Balance',
            ],
        ),
        (
            'Shotguns',
            [
                # Regular Legendaries
                'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Bandit_5_SledgesShotgun',
                'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Tediore_5_Deliverance',
                'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Torgue_5_Flakker',
                'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Jakobs_5_Striker',
                'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Hyperion_5_ConferenceCall',
            ],
            [
                # Uniques
                'GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra',
                'GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo',
                'GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper',
                'GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth',
                'GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion',
                'GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister',
                'GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra',
            ],
            [
                # Pearls
                'GD_Gladiolus_Weapons.Shotgun.SG_Hyperion_6_Butcher',
                'GD_Lobelia_Weapons.Shotguns.SG_Torgue_6_Carnage',
            ],
            [
                # Seraphs
                'GD_Orchid_RaidWeapons.Shotgun.Spitter.Orchid_Seraph_Spitter_Balance',
                'GD_Sage_RaidWeapons.Shotgun.Sage_Seraph_Interfacer_Balance',
                'GD_Aster_RaidWeapons.Shotguns.Aster_Seraph_Omen_Balance',
            ],
        ),
        (
            'SMG',
            [
                # Regular Legendaries
                'GD_Weap_SMG.A_Weapons_Legendary.SMG_Bandit_5_Slagga',
                'GD_Weap_SMG.A_Weapons_Legendary.SMG_Tediore_5_BabyMaker',
                'GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor',
                'GD_Weap_SMG.A_Weapons_Legendary.SMG_Maliwan_5_HellFire',
                'GD_Weap_SMG.A_Weapons_Legendary.SMG_Hyperion_5_Bitch',
            ],
            [
                # Uniques
                'GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch',
                'GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder',
                'GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch',
                'GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane',
                'GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce',
                'GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn',
                'GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit',
                'GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux',
                'GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk',
                'GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket',
                'GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc',
            ],
            [
                # Pearls
                'GD_Gladiolus_Weapons.SMG.SMG_Tediore_6_Avenger',
            ],
            [
                # Seraphs
                'GD_Orchid_RaidWeapons.SMG.Tattler.Orchid_Seraph_Tattler_Balance',
                'GD_Orchid_RaidWeapons.SMG.Actualizer.Orchid_Seraph_Actualizer_Balance',
                'GD_Aster_RaidWeapons.SMGs.Aster_Seraph_Florentine_Balance',
            ],
        ),
        (
            'SniperRifles',
            [
                # Regular Legendaries
                'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork',
                'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila',
                'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano',
                'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher',
                'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader',
            ],
            [
                # Uniques
                'GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun',
                'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge',
                'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo',
                'GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra',
                'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie',
                'GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel',
                'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar',
                'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth',
                'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser',
                'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow',
            ],
            [
                # Pearls
                'GD_Gladiolus_Weapons.sniper.Sniper_Maliwan_6_Storm',
                'GD_Lobelia_Weapons.sniper.Sniper_Jakobs_6_Godfinger',
            ],
            [
                # Seraphs
                'GD_Orchid_RaidWeapons.sniper.Patriot.Orchid_Seraph_Patriot_Balance',
                'GD_Sage_RaidWeapons.sniper.Sage_Seraph_HawkEye_Balance',
            ],
        ),
        ]:

    # First set up a hotfix for the base pool initialization
    initial_pool = []
    for legendary in legendaries:
        initial_pool.append((legendary, 1, 'WeaponBalanceDefinition'))
    for i in range(len(uniques) + len(pearls) + len(seraphs)):
        initial_pool.append((None, 0))
    hfs.add_level_hotfix('weapon_pool_clear_{}'.format(guntype.lower()),
        'WeaponPoolClear{}'.format(guntype),
        """,GD_Itempools.WeaponPools.Pool_Weapons_{}_06_Legendary,
        BalancedItems,,{}""".format(
            guntype,
            get_balanced_items(initial_pool),
            ))

    # Hotfixes to add uniques
    for (idx, unique) in enumerate(uniques):
        hotfix_id = 'unique_weap_add_{}_{}'.format(guntype.lower(), idx)
        unique_hotfixes.append(hotfix_id)
        hfs.add_level_hotfix(hotfix_id,
            'WeaponUniqueAdd{}'.format(guntype),
            """,GD_Itempools.WeaponPools.Pool_Weapons_{}_06_Legendary,
            BalancedItems[{}],,
            (
                ItmPoolDefinition=None,
                InvBalanceDefinition=WeaponBalanceDefinition'{}',
                Probability=(
                    BaseValueConstant=1,
                    BaseValueAttribute=None,
                    InitializationDefinition=None,
                    BaseValueScaleConstant=1
                ),
                bDropOnDeath=True
            )
            """.format(
                guntype,
                len(legendaries) + idx,
                unique
                ))

    # Hotfixes to add pearls
    for (idx, pearl) in enumerate(pearls):
        hotfix_id = 'pearl_weap_add_{}_{}'.format(guntype.lower(), idx)
        pearl_hotfixes.append(hotfix_id)
        hfs.add_level_hotfix(hotfix_id,
            'WeaponPearlAdd{}'.format(guntype),
            """,GD_Itempools.WeaponPools.Pool_Weapons_{}_06_Legendary,
            BalancedItems[{}],,
            (
                ItmPoolDefinition=None,
                InvBalanceDefinition=WeaponBalanceDefinition'{}',
                Probability=(
                    BaseValueConstant=1,
                    BaseValueAttribute=None,
                    InitializationDefinition=None,
                    BaseValueScaleConstant=1
                ),
                bDropOnDeath=True
            )
            """.format(
                guntype,
                len(legendaries) + len(uniques) + idx,
                pearl
                ))

    # Hotfixes to add seraphs
    for (idx, seraph) in enumerate(seraphs):
        hotfix_id = 'seraph_weap_add_{}_{}'.format(guntype.lower(), idx)
        seraph_hotfixes.append(hotfix_id)
        hfs.add_level_hotfix(hotfix_id,
            'WeaponSeraphAdd{}'.format(guntype),
            """,GD_Itempools.WeaponPools.Pool_Weapons_{}_06_Legendary,
            BalancedItems[{}],,
            (
                ItmPoolDefinition=None,
                InvBalanceDefinition=WeaponBalanceDefinition'{}',
                Probability=(
                    BaseValueConstant=1,
                    BaseValueAttribute=None,
                    InitializationDefinition=None,
                    BaseValueScaleConstant=1
                ),
                bDropOnDeath=True
            )
            """.format(
                guntype,
                len(legendaries) + len(uniques) + len(pearls) + idx,
                seraph
                ))

other.legendary_unique_adds = "\n\n".join(
        ['{}{}'.format(' '*(4*3), hfs.get_hotfix(hotfix_id).get_xml()) for hotfix_id in unique_hotfixes]
    )

other.legendary_pearl_adds = "\n\n".join(
        ['{}{}'.format(' '*(4*3), hfs.get_hotfix(hotfix_id).get_xml()) for hotfix_id in pearl_hotfixes]
    )

other.legendary_seraph_adds = "\n\n".join(
        ['{}{}'.format(' '*(4*3), hfs.get_hotfix(hotfix_id).get_xml()) for hotfix_id in seraph_hotfixes]
    )

# Legendary shield pool configuration.  Doing this a bit differently since there's
# not nearly as many shields to handle as weapons.

shields = {
    'GD_Itempools.ShieldPools.Pool_Shields_Absorption_06_Legendary': [
        ('1340', 2, 'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340'),
        ('equitas', 3, 'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas'),
        ('sponge', 4, 'GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance'),
        ],
    'GD_Itempools.ShieldPools.Pool_Shields_Booster_06_Legendary': [
        ('potogold', 1, 'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold'),
        ('bigboomblaster', 2, 'GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance'),
        ],
    'GD_Itempools.ShieldPools.Pool_Shields_Chimera_06_Legendary': [
        ('evolution', 1, 'GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance')
        ],
    'GD_Itempools.ShieldPools.Pool_Shields_Juggernaut_06_Legendary': [
        ('hoplite', 1, 'GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance'),
        ],
    'GD_Itempools.ShieldPools.Pool_Shields_NovaShields_Explosive_06_Legendary': [
        ('deadlybloom', 0, 'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom'),
        ],
    'GD_Itempools.ShieldPools.Pool_Shields_Roid_06_Legendary': [
        ('order', 1, 'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order'),
        ('lovethumper', 2, 'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper'),
        ('punchee', 3, 'GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance'),
        ],
    'GD_Itempools.ShieldPools.Pool_Shields_Standard_06_Legendary': [
        ('manlyman', 1, 'GD_Orchid_Shields.A_Item_Custom.S_BladeShield'),
        ('roughrider', 2, 'GD_Sage_Shields.A_Item_Custom.S_BucklerShield'),
        ('antagonist', 3, 'GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance'),
        ('blockade', 4, 'GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance'),
        ],
    }
for (pool, shieldlist) in shields.items():
    for (label, index, shieldname) in shieldlist:
        set_bi_item_pool('shield_{}'.format(label),
            pool,
            index,
            shieldname,
            invbalance='InventoryBalanceDefinition')

# Save our current hotfixes
orig_hfs = hfs

# Set up Boss/Miniboss unique drops.
boss_drops = {}
line_prefix = ''
line_suffix = ''
hotfix_activated = True
for (label, key, unique_pct, rare_pct) in [
        ('Guaranteed', 'guaranteed', 1, 1),
        ('Very Improved', 'veryimproved', .5, .75),
        ('Improved', 'improved', .33, .60),
        ('Slightly Improved', 'slight', .22, .45),
        ('Stock Equip', 'stock', .1, .33),
        ]:

    # Set up a new hotfixes object so we don't have to fiddle with hotfix IDs
    hfs = Hotfixes(nameprefix='ApocBoss{}'.format(key.capitalize()))

    # Midge-mong uses a KerBlaster.  The rider is a generic Badass Midget, but fortunately
    # no other Badass Midgets can spawn in Cove_P.  So just fiddle with the pools via
    # hotfix and we're good to go. (Cove_P pool 0)

    setup_boss_pool('midgemong_pool_0', 'Cove_P', other.level_pool_0,
            badass.equip_pool_smg,
            [
                ('GD_Itempools.Runnables.Pool_WarMong', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('midgemong_pool_1',
            'GD_Population_Midget.Balance.PawnBalance_MidgetBadass',
            0,
            other.level_pool_0,
            level='Cove_P',
            activated=hotfix_activated)

    hfs.add_level_hotfix('midgemong_clean_pool', 'Midge',
            """Cove_P,
            GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_Warmong,
            DefaultItemPoolList,,
            ()""",
            activated=hotfix_activated)

    # Captain Flynt (SouthernShelf_P pool 0)

    setup_boss_pool('flynt_pool_0', 'SouthernShelf_P', other.level_pool_0,
            None,
            [
                ('GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Maliwan_5_ThunderballFists', 1, 'WeaponBalanceDefinition'),
                ('GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox', 1, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_prob('flynt_pool_1',
            'GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt',
            0,
            level='SouthernShelf_P',
            activated=hotfix_activated)

    set_dipl_item_prob('flynt_pool_2',
            'GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt',
            3,
            level='SouthernShelf_P',
            activated=hotfix_activated)

    set_dipl_item_pool('flynt_pool_3',
            'GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt',
            2,
            other.level_pool_0,
            level='SouthernShelf_P',
            activated=hotfix_activated)

    # Bad Maw - UCP adds Deliverance, so use that. (Frost_P pool 0)

    setup_boss_pool('badmaw_pool_0', 'Frost_P', other.level_pool_0,
            badass.equip_pool_shotguns,
            [
                ('GD_Itempools.Runnables.Pool_Tumba', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_pt_cipl_item_pool('badmaw_pool_1',
            'GD_Population_Nomad.Balance.PawnBalance_BadMaw',
            0, 0,
            other.level_pool_0,
            level='Frost_P',
            activated=hotfix_activated)

    set_pt_cipl_item_pool('badmaw_pool_2',
            'GD_Population_Nomad.Balance.PawnBalance_BadMaw',
            1, 0,
            other.level_pool_0,
            level='Frost_P',
            activated=hotfix_activated)

    set_pt_cipl_item_prob('badmaw_pool_3',
            'GD_Population_Nomad.Balance.PawnBalance_BadMaw',
            0, 2,
            level='Frost_P',
            activated=hotfix_activated)

    set_pt_cipl_item_prob('badmaw_pool_4',
            'GD_Population_Nomad.Balance.PawnBalance_BadMaw',
            1, 2,
            level='Frost_P',
            activated=hotfix_activated)

    # Assassin Common - remove Emperor from the shared loot pool

    set_bi_item_prob('assassin_pool_0',
        'GD_Itempools.Runnables.Pool_FourAssassins',
        0,
        level='SouthpawFactory_P',
        activated=hotfix_activated)

    # Assassin Wot (using Runnables)
    # Note that for the assassins, we're not using our level_pools, since the
    # Runnables for these are only used by their Digistruct counterparts, so
    # we don't have to worry about tainting the pools.

    setup_boss_pool('wot_pool_0', 'SouthpawFactory_P',
            'GD_Itempools.Runnables.Pool_AssassinWot',
            badass.equip_pool_smg,
            [
                ('GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce', rare_pct, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor', rare_pct/4, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_prob('wot_pool_1',
        'GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1',
        0,
        level='SouthpawFactory_P',
        activated=hotfix_activated)

    set_dipl_item_prob('wot_pool_2',
        'GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1',
        2,
        level='SouthpawFactory_P',
        prob=1,
        activated=hotfix_activated)

    # Assassin Oney (using Runnables)

    setup_boss_pool('oney_pool_0', 'SouthpawFactory_P',
            'GD_Itempools.Runnables.Pool_AssassinOney',
            badass.equip_pool_only_shotguns,
            [
                ('GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge', rare_pct, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor', rare_pct/4, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_prob('oney_pool_1',
        'GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2',
        1,
        level='SouthpawFactory_P',
        activated=hotfix_activated)

    set_dipl_item_prob('oney_pool_2',
        'GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2',
        3,
        level='SouthpawFactory_P',
        prob=1,
        activated=hotfix_activated)

    # Assassin Reeth (melee only, so only a pool setup here) (using Runnables)

    setup_boss_pool('reeth_pool_0', 'SouthpawFactory_P',
            'GD_Itempools.Runnables.Pool_AssassinReeth',
            None,
            [
                ('GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge', 1, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor', .25, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    # Assassin Rouf (using Runnables)

    setup_boss_pool('rouf_pool_0', 'SouthpawFactory_P',
            'GD_Itempools.Runnables.Pool_AssassinRouf',
            badass.equip_pool_only_shotguns,
            [
                ('GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog', rare_pct, 'WeaponBalanceDefinition'),
                ('GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor', rare_pct/4, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_prob('rouf_pool_1',
        'GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4',
        0,
        level='SouthpawFactory_P',
        activated=hotfix_activated)

    set_dipl_item_prob('rouf_pool_2',
        'GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4',
        2,
        level='SouthpawFactory_P',
        prob=1,
        activated=hotfix_activated)

    # Incinerator Clayton (IceCanyon_P pool 0)

    setup_boss_pool('clayton_pool_0', 'IceCanyon_P', other.level_pool_0,
            badass.pool_shields,
            [
                ('GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix', unique_pct, 'InventoryBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('clayton_pool_1',
            'GD_Population_Psycho.Balance.Unique.PawnBalance_IncineratorVanya_Combat',
            0,
            other.level_pool_0,
            level='IceCanyon_P',
            activated=hotfix_activated)

    set_bi_item_prob('clayton_pool_2',
        'GD_Itempools.Runnables.Pool_Clayton',
        1,
        level='IceCanyon_P',
        activated=hotfix_activated)

    # Flinter (Dam_P pool 0)

    setup_boss_pool('flinter_pool_0', 'Dam_P', other.level_pool_0,
            badass.equip_pool_ar,
            [
                ('GD_CustomItemPools_MainGame.Assassin.Head9', rare_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('flinter_pool_1',
            'GD_Population_Rat.Balance.Unique.PawnBalance_RatEasterEgg',
            0,
            other.level_pool_0,
            level='Dam_P',
            activated=hotfix_activated)

    set_dipl_item_prob('flinter_pool_2',
        'GD_Population_Rat.Balance.Unique.PawnBalance_RatEasterEgg',
        2,
        level='Dam_P',
        activated=hotfix_activated)

    # Mad Mike (Dam_P pool 1)

    # Let's make Mike cap out at 50% for Madhous!, since his real pleasures
    # in life are those rocket launchers...
    if unique_pct > .5:
        mike_pct = .5
    else:
        mike_pct = unique_pct

    setup_boss_pool('mad_mike_pool_0', 'Dam_P', other.level_pool_1,
            badass.equip_pool_launchers,
            [
                ('GD_Itempools.Runnables.Pool_MadDog', mike_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('mad_mike_pool_1',
            'GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike',
            0,
            other.level_pool_1,
            level='Dam_P',
            activated=hotfix_activated)

    # UCP sets CustomItemPoolList to add the MadHous, but since we're
    # overriding the equip pool anyway, just clear out that UCP edit.
    hfs.add_level_hotfix('mad_mike_pool_2', 'MadMike',
        """Dam_P,
        GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike,
        PlayThroughs[0].CustomItemPoolList,,
        ()""",
        activated=hotfix_activated)

    # Prospector Zeke (TundraExpress_P pool 0)

    setup_boss_pool('zeke_pool_0', 'TundraExpress_P', other.level_pool_0,
            badass.equip_pool_ar,
            [
                ('GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork', unique_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('zeke_pool_1',
            'GD_Population_Nomad.Balance.Unique.PawnBalance_Prospector',
            0,
            other.level_pool_0,
            level='TundraExpress_P',
            activated=hotfix_activated)

    set_dipl_item_prob('zeke_pool_2',
        'GD_Population_Nomad.Balance.Unique.PawnBalance_Prospector',
        2,
        level='TundraExpress_P',
        activated=hotfix_activated)

    # Laney (using her own pool)

    setup_boss_pool('laney_pool_0', 'Fridge_P',
            'GD_Itempools.Runnables.Pool_Laney',
            badass.equip_pool_pistols,
            [
                ('GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Bandit_5_Gub', unique_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_prob('laney_pool_1',
        'GD_Population_Rat.Balance.Unique.PawnBalance_Laney',
        0,
        level='Fridge_P',
        activated=hotfix_activated)

    set_dipl_item_prob('laney_pool_2',
        'GD_Population_Rat.Balance.Unique.PawnBalance_Laney',
        2,
        level='Fridge_P',
        prob=1,
        activated=hotfix_activated)

    # Smash-Head (Fridge_P pool 0)

    setup_boss_pool('smashhead_pool_0', 'Fridge_P', other.level_pool_0,
            badass.equip_pool_launchers,
            [
                ('GD_Weap_Shotgun.A_Weapons_Legendary.SG_Bandit_5_SledgesShotgun', unique_pct, 'WeaponBalanceDefinition'),
                ('GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster', rare_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('smashhead_pool_1',
            'GD_Population_Goliath.Balance.Unique.PawnBalance_SmashHead',
            0,
            other.level_pool_0,
            level='Fridge_P',
            activated=hotfix_activated)

    set_dipl_item_prob('smashhead_pool_2',
        'GD_Population_Goliath.Balance.Unique.PawnBalance_SmashHead',
        1,
        level='Fridge_P',
        activated=hotfix_activated)

    set_dipl_item_prob('smashhead_pool_3',
        'GD_Population_Goliath.Balance.Unique.PawnBalance_SmashHead',
        2,
        level='Fridge_P',
        activated=hotfix_activated)

    # Bagman (Luckys_P pool 0)

    setup_boss_pool('bagman_pool_0', 'Luckys_P', other.level_pool_0,
            badass.pool_shields,
            [
                ('GD_Itempools.Runnables.Pool_Bagman', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('bagman_pool_1',
            'GD_Population_Engineer.Balance.Unique.PawnBalance_Leprechaun',
            2,
            other.level_pool_0,
            level='Luckys_P',
            activated=hotfix_activated)

    set_dipl_item_prob('bagman_pool_2',
        'GD_Population_Engineer.Balance.Unique.PawnBalance_Leprechaun',
        1,
        level='Luckys_P',
        activated=hotfix_activated)

    # Muscles (Grass_Cliffs_P pool 0)

    setup_boss_pool('muscles_pool_0', 'Grass_Cliffs_P', other.level_pool_0,
            badass.equip_pool_ar,
            [
                ('GD_Weap_Shotgun.A_Weapons_Legendary.SG_Bandit_5_SledgesShotgun', unique_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('muscles_pool_1',
            'GD_Population_Bruiser.Balance.PawnBalance_Bruiser_Muscles',
            0,
            other.level_pool_0,
            level='Grass_Cliffs_P',
            activated=hotfix_activated)

    set_dipl_item_prob('muscles_pool_2',
        'GD_Population_Bruiser.Balance.PawnBalance_Bruiser_Muscles',
        1,
        level='Grass_Cliffs_P',
        activated=hotfix_activated)

    # Foreman Jasper (HyperionCity_P pool 0)

    setup_boss_pool('foreman_pool_0', 'HyperionCity_P', other.level_pool_0,
            badass.pool_shields,
            [
                ('GD_Itempools.Runnables.Pool_Foreman', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('foreman_pool_1',
            'GD_Population_Engineer.Balance.Unique.PawnBalance_Foreman',
            2,
            other.level_pool_0,
            level='HyperionCity_P',
            activated=hotfix_activated)

    # Gettle (uses own pool)

    setup_boss_pool('gettle_pool_0', 'Interlude_P',
            'GD_Itempools.Runnables.Pool_Gettle',
            badass.equip_pool_ar,
            [
                ('GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila', unique_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_prob('gettle_pool_1',
        'GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle',
        0,
        level='Interlude_P',
        activated=hotfix_activated)

    set_dipl_item_prob('gettle_pool_2',
        'GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle',
        2,
        level='Interlude_P',
        prob=1,
        activated=hotfix_activated)

    # Mobley (Interlude_P pool 0)

    setup_boss_pool('mobley_pool_0', 'Interlude_P', other.level_pool_0,
            badass.equip_pool_pistols,
            [
                ('GD_Itempools.Runnables.Pool_Mobley', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('mobley_pool_1',
            'GD_Population_Marauder.Balance.Unique.PawnBalance_Mobley',
            3,
            other.level_pool_0,
            level='Interlude_P',
            activated=hotfix_activated)

    set_dipl_item_prob('mobley_pool_2',
        'GD_Population_Marauder.Balance.Unique.PawnBalance_Mobley',
        0,
        level='Interlude_P',
        activated=hotfix_activated)

    # Mick Zaford (Interlude_P pool 1)

    setup_boss_pool('zaford_pool_0', 'Interlude_P', other.level_pool_1,
            badass.equip_pool_smg,
            [
                ('GD_Itempools.Runnables.Pool_MickZaford', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('zaford_pool_1',
            'GD_Population_Marauder.Balance.Unique.PawnBalance_MickZaford_Combat',
            3,
            other.level_pool_1,
            level='Interlude_P',
            activated=hotfix_activated)

    set_dipl_item_prob('zaford_pool_2',
        'GD_Population_Marauder.Balance.Unique.PawnBalance_MickZaford_Combat',
        0,
        level='Interlude_P',
        activated=hotfix_activated)

    # Jimbo & Tector Hodunk (Interlude_P pool 2)

    setup_boss_pool('hodunk_pool_0', 'Interlude_P', other.level_pool_2,
            badass.equip_pool_only_shotguns,
            [
                ('GD_Itempools.Runnables.Pool_TectorHodunk', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('hodunk_pool_1',
            'GD_Population_Marauder.Balance.Unique.PawnBalance_TectorHodunk_Combat',
            3,
            other.level_pool_2,
            level='Interlude_P',
            activated=hotfix_activated)

    set_dipl_item_prob('hodunk_pool_2',
        'GD_Population_Marauder.Balance.Unique.PawnBalance_TectorHodunk_Combat',
        0,
        level='Interlude_P',
        activated=hotfix_activated)

    # Jimbo Hodunk equip fix (shouldn't actually have a gun equip)

    set_dipl_item_prob('hodunk_pool_3',
        'GD_Population_Marauder.Balance.Unique.PawnBalance_JimboRiding',
        0,
        level='Interlude_P',
        activated=hotfix_activated)

    # Deputy Winger (Grass_Lynchwood_P pool 0)

    setup_boss_pool('winger_pool_0', 'Grass_Lynchwood_P', other.level_pool_0,
            badass.pool_shields,
            [
                ('GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order', rare_pct, 'InventoryBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('winger_pool_1',
            'GD_Population_Sheriff.Balance.PawnBalance_Deputy',
            1,
            other.level_pool_0,
            level='Grass_Lynchwood_P',
            activated=hotfix_activated)

    set_bi_item_prob('winger_pool_2',
        'GD_CustomItemPools_MainGame.Assassin.PurplePale',
        0,
        level='Grass_Lynchwood_P',
        activated=hotfix_activated)

    # Sheriff of Lynchwood (Grass_Lynchwood_P pool 1)

    setup_boss_pool('sheriff_pool_0', 'Grass_Lynchwood_P', other.level_pool_1,
            badass.equip_pool_pistols,
            [
                ('GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law', rare_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('sheriff_pool_1',
            'GD_Population_Sheriff.Balance.PawnBalance_Sheriff',
            0,
            other.level_pool_1,
            level='Grass_Lynchwood_P',
            activated=hotfix_activated)

    set_bi_item_prob('sheriff_pool_2',
        'GD_Itempools.Runnables.Pool_Sheriff',
        1,
        level='Grass_Lynchwood_P',
        activated=hotfix_activated)

    # Mortar (CraterLake_P pool 0)

    setup_boss_pool('mortar_pool_0', 'CraterLake_P', other.level_pool_0,
            badass.equip_pool_only_shotguns,
            [
                ('GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher', unique_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('mortar_pool_1',
            'GD_Population_Rat.Balance.Unique.PawnBalance_Mortar',
            0,
            other.level_pool_0,
            level='CraterLake_P',
            activated=hotfix_activated)

    set_dipl_item_prob('mortar_pool_2',
        'GD_Population_Rat.Balance.Unique.PawnBalance_Mortar',
        3,
        level='CraterLake_P',
        activated=hotfix_activated)

    # Hunter Hellquist (Fyrestone_P pool 0)

    setup_boss_pool('hunter_pool_0', 'Fyrestone_P', other.level_pool_0,
            badass.pool_shields,
            [
                ('GD_Itempools.Runnables.Pool_HunterHellquist', unique_pct, None),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('hunter_pool_1',
            'GD_Population_Engineer.Balance.Unique.PawnBalance_DJHyperion',
            1,
            other.level_pool_0,
            level='Fyrestone_P',
            activated=hotfix_activated)

    set_dipl_item_prob('hunter_pool_2',
        'GD_Population_Engineer.Balance.Unique.PawnBalance_DJHyperion',
        2,
        level='Fyrestone_P',
        activated=hotfix_activated)

    # Bone Head 2.0 (Stockade_P pool 0)

    setup_boss_pool('bonehead2_pool_0', 'Stockade_P', other.level_pool_0,
            badass.equip_pool_ar,
            [
                ('GD_Itempools.Runnables.Pool_Bonehead2', rare_pct, None),
                ('GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Vladof_5_Sherdifier', unique_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('bonehead2_pool_1',
            'GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2',
            0,
            other.level_pool_0,
            level='Stockade_P',
            activated=hotfix_activated)

    set_dipl_item_prob('bonehead2_pool_2',
        'GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2',
        1,
        level='Stockade_P',
        activated=hotfix_activated)

    set_dipl_item_prob('bonehead2_pool_3',
        'GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2',
        3,
        level='Stockade_P',
        activated=hotfix_activated)

    # No-Beard (Orchid_OasisTown_P pool 0)
    # Different from the rest, because he already equips a version of the
    # Stinkpot at 100%.  We convert that to the "real" Stinkpot and keep the
    # 100% equip rate.  This means that this could live outside our boss MUT
    # category, but it's a bit cleaner to keep it in here.

    setup_boss_pool('nobeard_pool_0', 'Orchid_OasisTown_P', other.level_pool_0,
            None,
            [
                ('GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot', 1, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('nobeard_pool_1',
            'GD_Orchid_Pop_NoBeard.PawnBalance_Orchid_NoBeard',
            0,
            other.level_pool_0,
            level='Orchid_OasisTown_P',
            activated=hotfix_activated)

    set_dipl_item_prob('nobeard_pool_2',
        'GD_Orchid_Pop_NoBeard.PawnBalance_Orchid_NoBeard',
        1,
        level='Orchid_OasisTown_P',
        activated=hotfix_activated)

    # Benny the Booster (Orchid_OasisTown_P pool 1)

    setup_boss_pool('benny_pool_0', 'Orchid_OasisTown_P', other.level_pool_1,
            badass.equip_pool_ar,
            [
                ('GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk', rare_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('benny_pool_1',
            'GD_Orchid_Pop_Deserters.Deserter1.PawnBalance_Orchid_Deserter1',
            0,
            other.level_pool_1,
            level='Orchid_OasisTown_P',
            activated=hotfix_activated)

    set_dipl_item_prob('benny_pool_2',
        'GD_Orchid_Pop_Deserters.Deserter1.PawnBalance_Orchid_Deserter1',
        1,
        level='Orchid_OasisTown_P',
        activated=hotfix_activated)

    # Sandman / Big Sleep (Orchid_Caves_P pool 0)

    hfs.add_level_hotfix('bigsleep_pool_0', 'BigSleepDrop',
        """Orchid_Caves_P,
        GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_BigSleep,
        DefaultItemPoolList[1].PoolProbability.BaseValueConstant,,0""",
        activated=hotfix_activated)

    setup_boss_pool('sandman_pool_0', 'Orchid_Caves_P', other.level_pool_0,
            badass.equip_pool_ar,
            [
                ('GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder', rare_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('sandman_pool_1',
            'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman',
            0,
            other.level_pool_0,
            level='Orchid_Caves_P',
            activated=hotfix_activated)

    set_dipl_item_pool('sandman_pool_2',
            'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman_MarauderMaster',
            0,
            other.level_pool_0,
            level='Orchid_Caves_P',
            activated=hotfix_activated)

    set_dipl_item_pool('sandman_pool_3',
            'GD_Orchid_Pop_Sandman.Balance.PawnBalance_Orchid_Sandman_Solo',
            0,
            other.level_pool_0,
            level='Orchid_Caves_P',
            activated=hotfix_activated)

    # DJ Tanner (Orchid_Spire_P pool 0)

    setup_boss_pool('tanner_pool_0', 'Orchid_Spire_P', other.level_pool_0,
            badass.pool_shields,
            [
                ('GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal', unique_pct, 'InventoryBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('tanner_pool_1',
            'GD_Orchid_Pop_PirateRadioGuy.PawnBalance_Orchid_PirateRadioGuy',
            1,
            other.level_pool_0,
            level='Orchid_Spire_P',
            activated=hotfix_activated)

    set_dipl_item_prob('tanner_pool_2',
        'GD_Orchid_Pop_PirateRadioGuy.PawnBalance_Orchid_PirateRadioGuy',
        2,
        level='Orchid_Spire_P',
        activated=hotfix_activated)

    # Toothless Terry (Orchid_ShipGraveyard_P pool 0)
    # Using unique rather than rare, to make launcher pretty common still, since that's
    # sort of his thing.

    setup_boss_pool('terry_pool_0', 'Orchid_ShipGraveyard_P', other.level_pool_0,
            badass.equip_pool_launchers,
            [
                ('GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel', unique_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('terry_pool_1',
            'GD_Orchid_Pop_Deserters.Deserter3.PawnBalance_Orchid_Deserter3',
            0,
            other.level_pool_0,
            level='Orchid_ShipGraveyard_P',
            activated=hotfix_activated)

    set_dipl_item_prob('terry_pool_2',
        'GD_Orchid_Pop_Deserters.Deserter3.PawnBalance_Orchid_Deserter3',
        1,
        level='Orchid_ShipGraveyard_P',
        activated=hotfix_activated)

    # P3RV-E (Orchid_Refinery_P pool 0)

    setup_boss_pool('pervy_pool_0', 'Orchid_Refinery_P', other.level_pool_0,
            badass.equip_pool_ar,
            [
                ('GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch', rare_pct, 'WeaponBalanceDefinition'),
            ],
            activated=hotfix_activated)

    set_dipl_item_pool('pervy_pool_1',
            'GD_Orchid_Pop_Pervbot.PawnBalance_Orchid_Pervbot',
            0,
            other.level_pool_0,
            level='Orchid_Refinery_P',
            activated=hotfix_activated)

    set_dipl_item_prob('pervy_pool_2',
        'GD_Orchid_Pop_Pervbot.PawnBalance_Orchid_Pervbot',
        2,
        level='Orchid_Refinery_P',
        activated=hotfix_activated)

    # Generate the section string
    with open('input-file-bosses.txt', 'r') as df:
        boss_drops[key] = df.read().format(
                boss_label='{} ({}% Uniques, {}% Rares)'.format(
                    label, round(unique_pct*100), round(rare_pct*100)),
                line_prefix=line_prefix,
                line_suffix=line_suffix,
                hotfixes=hfs,
                regular=regular,
                badass=badass,
                other=other,
                unique_pct=unique_pct,
                rare_pct=rare_pct,
                )

    line_prefix = '#'
    line_suffix = '<off>'
    hotfix_activated = False

###
### Generate the mod string
###

with open('input-file-mod.txt') as df:
    mod_str = df.read().format(
        mod_name=mod_name,
        mod_version=mod_version,
        hotfixes=orig_hfs,
        regular=regular,
        badass=badass,
        other=other,
        rarity_excellent=rarity_sections['excellent'],
        rarity_better=rarity_sections['better'],
        rarity_stock=rarity_sections['stock'],
        boss_drops_guaranteed=boss_drops['guaranteed'],
        boss_drops_veryimproved=boss_drops['veryimproved'],
        boss_drops_improved=boss_drops['improved'],
        boss_drops_slightimproved=boss_drops['slight'],
        boss_drops_stock=boss_drops['stock'],
        )

###
### Output to a file.
###

with open(output_filename, 'w') as df:
    df.write(mod_str)
print('Wrote mod file to: {}'.format(output_filename))
