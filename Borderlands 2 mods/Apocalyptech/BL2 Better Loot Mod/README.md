BL2 Better Loot Mod by Apocalyptech
===================================

This mod aims to make loot in Borderlands 2 "better" in general.  It's
essentially a cheat mod, intended for those BL2 players like myself who
tend to play in Normal most of the time, dislike grinding, get bored easily
by the uninteresting and drab loot that typically gets dropped in-game, and
who often end up just resorting to Gibbed to be able to play around with
some better gear.  The goal, personally, was to get the loot drops in-game
to a point where I never felt tempted to open up Gibbed.

This patch is set up to play nicely with FilterTool, and basically
everything in here can be toggled on or off inside FilterTool as you'd
hope, on an item-by-item basis.  Basically every bullet point in the
"Overview" section is its own "folder" once imported into FilterTool.

Note that the Hammerlock and Tiny Tina DLCs were already quite generous
with loot, compared to the rest of the game, and this mod ends up making
those DLCs a bit ridiculous with loot.  I'll probably not bother trying
to stem that tide, though, so just enjoy the overabundance of loot!

Usage/Installation
------------------

The recommended way to use this mod is with FilterTool/UCP.  In FilterTool,
select `Developer Tools` -> `Add Single Mod` and then select the file
file `BL2 Better Loot Mod by Apocalyptech - FilterTool and UCP Compat`
(without any extensions).  You'll have a new folder for this mod underneath
the `mods` folder at the bottom, and can turn parts on or off at will.

*Note:* At the moment this mod updates a few vars that UCP does as well, and
FilterTool will complain because more than one mod is touching the same
stuff.  I'll figure that out in a bit - for now, I think it's all pretty
minor stuff, like the UCP sections which add gear to boss pools, etc.

If for whatever reason you don't want to use FilterTool/UCP, there is also
a standalone version at `BL2 Better Loot Mod by Apocalyptech - Standalone`.
Simply copy that file into the game's `steamassets/binaries` directory with
an easy-to-type filename, and then run `exec <filename>` from the console
to load it on its own.  It works quite well by itself.

The reason it's split up this way is due to how hotfixes are processed.  If
you're using UCP/FilterTool, all the default Gearbox hotfixes are handled
for you.  But if you want to just use this mod for whatever reason, it needs
to take care of the default hotfixes itself, hence the different files.

Mod Overview
------------

Specifically, this mod does the following:

* Adds all legendaries/uniques/pearls/seraph items (weapons, grenade mods,
  class mods, shields, relics) into the global "legendary" loot pools, so
  you'll start seeing those much more frequently.
* Loot will skew much more rare, in general.  You should expect to see
  those legendaries/uniques/pearls/seraphs far more frequently than in
  vanilla BL2.
* "Regular" treasure chests will always provide at least blue-rarity gear,
  and has a decent chance of including stuff from the legendary pools.
* "Epic" treasure chests have an extremely high probability of dropping
  from the legendary pools.
* Dice Chests (from the Tiny Tina DLC) will have a small chance of containing
  legendary loot on a "very high" roll.
* When lockers spawn gear, they will always be blue-rarity.  *(Previously
  lockers had a chance to spawn even legendaries, so some could potentially
  see this as a drawback)*
* Adds the "Alignment" Class Mods from the Dragon Keep DLC into the global
  Class Mod drop pools (and makes those COMs always drop at at least blue
  rarity).
* Adds Gemstone-rarity weapons into the E-Tech weapon pools.
* Darts and Spikers drop far less frequently in the E-Tech pools.  *(I
  suspect this might annoy some folks; I could probably be convinced to
  undo that)*
* Makes Eridium drop 3x more often
* Makes Torgue Tokens more numerous when dropped
* Bosses are guaranteed to drop as many items from their legendary/unique
  pool as are in that pool.
  * Bosses with just a single unique/legendary drop will therefore be
    guaranteed to drop that item.
  * If a boss has more than one in their drop pool, you may get duplicates
    of one rather than one of each.
  * Normalized the chances of boss-item drops, for the handful of bosses
    whose loot probabilities weren't already equal.
* Raid Bosses will drop better loot, and will drop as many legendary/unique/etc
  items as are in their pool.  (Seraph Crystal drops are increased as well,
  and Guardians will drop Seraph Crystals even in Normal mode).  I still have a
  couple to go through; the ones currently in place are:
  * Terramorphous
  * Vermivorous
  * Hyperius
  * Master Gee
  * Pyro Pete
  * Dexiduous
  * Voracidous
* Fixes/Changes to some enemies' drop pools:
  * Witch Doctors will drop an Eridium stick, and have a pretty good chance
    of dropping a Relic as well.
  * Enemies changed to drop from from the Badass loot pool, rather than the
    standard enemy pool:
    * Badass Boroks
    * Bulstross
    * Arguk the Butcher
    * Skeleton Giants *(as if the Dragon Keep DLC needed more loot)*
* Remove early-game loot restrictions.  This is actually a superset of the
  similar feature already present in UCP 4.0.  This version enables spawning
  of basically everything from the beginning, including all grenade types,
  relics, class mods, rocket launchers, etc.  Both this and the UCP 4.0
  "Remove Loot restriction in the beginning areas" mods can be active at the
  same time with no ill effects -- it'll just mean that the relevant commands
  get executed twice.  Note that if you *don't* have either this or UCP
  enabled on your game, the early game will end up dropping *no* gear, due
  to our rarity changes.
* Optionally, I've left in some statements which cause all enemies to
  always drop gear, and always drop five items rather than just one.  This
  is disabled by default and would have to be enabled manually via FilterTool
  -- I'd basically just been using them to test out my custom loot pools by
  having a larger sample size.

Compatibility
-------------

This mod is mostly compatible with UCP 4.0, though there's a few instances of
UCP and this mod writing to the same values (mostly to do with boss drops
and the like).  I do plan to go through and figure out a good way to coexist
with UCP so that I'm not writing to the same stuff, but I haven't gone through
to do that yet.  Stuff in UCP's "Specific Loot Changes" folder will be the
likeliest culprits.  I'll be looking into that in a bit.

Obviously this will conflict with other mods which play with the same
variables.  I know that Hemaxhu's "Better White Chests" would conflict with
this, for instance, and possibly other mods in Hemaxhu's "Chest Mods"
folder.  FromDarkHell's collection in the "Loot Drops" folder likewise will
probably conflict.

In terms of loot compatibility, I'm pretty sure that this mod makes the
"Vault Hunter's Relic" completely useless, but if you're using this mod,
you certainly won't miss it.

Loot Purposefully Excluded from Pools
-------------------------------------

There's some gear which I felt shouldn't be in the pools at all.  I am
quite willing to hear counterarguments; my mind could probably be pretty
easily persuaded otherwise if someone feels strongly about it.

* Cracked Sash (Shield)
* GOTY/Preorder/Whatever starting game loot:
  * "Gearbox" themed guns (AR/SMG/Sniper)
  * Contraband Sky Rocket
  * Vault Hunter's Relic
* Captain Blade's Midnight Star
* Blue-rarity Magic Missile *(purple rarity will still spawn -- they're
  technically different items)*
* "ERROR MESSAGE" Ahab (the one used by Master Gee).  Regular Ahabs will
  still spawn, though.
* Possibly one or two other guns as well -- I didn't think to keep track at
  first.

There's also a few drop pools / containers / etc which I've purposefully
left alone:

* White Chests
* Money Boxes
* Laundry Machines / Toilets / Cardboard Boxes
* Dumpsters
* Loot Midgets

Some other stuff not done:

* Scaylion drops are rather anemic compared to everything else in the
  Hammerlock DLC, but the Hammerlock DLC is kind of ludicrous with loot
  anyway, so I'm leaving them the way they are.
* Badass Giant Burning Broomsticks will continue to drop from the standard
  enemy pool rather than the badass pool.  There's dozens of those things
  all at once and it'd be ridiculous.

TODO
----

* Test interactions with UCP - make sure we're not stepping on any toes.
* Balancing!  This mod is obviously very cheaty/OP, but I don't want it to
  be completely ludicrous.  I'd like it to still feel a bit special when
  the Very Good loot gets dropped, while at the same time providing a steady
  supply of fun gear.  Obviously this is very much down to personal
  preference.  Regardless, I've done extremely little actual playtesting
  with the current drop weights.
* Boss drop counts for DLC bosses
* Can we increase boss drop counts depending on player count?
* I'm not actually terribly interested in changing this, but I'd love to
  know how the gear is allocated for the miscellaneous smaller containers
  throughout the game, such as those regular "white" chests (which
  more often than not just have ammo), cardboard boxes, washing machines,
  toilets, etc.  Nothing I've found seems to affect them.  Given the rest
  of what this mod does, it hardly matters, but my curiosity remains
  piqued.  I do know how to update dumpsters, but I left them alone on
  purpose.
* Untested components from Torgue DLC *(I'm afraid that's my least favorite
  DLC, to the point of not really liking it much, so I suspect that these
  may go untouched)*:
  * Pyro Pete's initial non-raid drops
  * Piston drops (just Slow Hand, I figure the mini-lootsplosion after is
    good enough to not bother tweaking his actual drop any more)
  * Torgue Biker Gang drops are a little weird - there's an extra drop which
    happens outside of their weighted drop pool, but I can't seem to figure
    out where that is.
  * I think Biker Badasses, etc, have pretty anemic drops at the moment.
* Add in level names to our hotfixes which could technically use them
* Also maybe set up our own prefix on all our hotfix names, so there's very
  little chance of ever conflicting with someone else's names.

Mod Construction / Implementation Details
-----------------------------------------

I actually generate this mod using a simple little Python script named
`generate-source.py`, which enables me to do things like set the rarity
drop levels from a single location at the top of the file, and have it
apply to a number of different objects throughout the game.  That script
outputs to a very human-readable multiline text file which can't actually
be read directly by FilterTool/Borderlands, and must then be processed by
my `conv_to_mod.py` script which you'll find in the parent directory.

To generate the end result file, I actually run the small shell script
`create.sh` in this directory, which just does the following:

    ./generate-source.py && \
        ../conv_to_mod.py -f "BL2 Better Loot Mod by Apocalyptech - FilterTool and UCP Compat" && \
        ../conv_to_mod.py -f "BL2 Better Loot Mod by Apocalyptech - Standalone"

Credits
-------

I've taken various ideas and at least one direct copy and paste from UCP,
and from various other mods which had similar goals as what I was looking
for:

* Setting guaranteed drops for the vast majority of bosses in-game, via
  two nicely-concise statements, came from JimRaven's "FarmFest"
* Orudeon's "Gemstone Loot Pools" clued me in that the main Gemstone pool in
  the Tiny Tina DLC is heavily weighted towards Pistols.
* *(will have to go through and see what else...)*

I'd also like to thank the fine folks in Shadow's Evil Hideout #borderlands-modding
Discord channel for putting up with all my noobish questions.
