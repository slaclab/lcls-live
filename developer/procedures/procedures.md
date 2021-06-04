# Procedures




## lcls-lattice updating


All lattice files are hosted on GitHub at https://github.com/slaclab/lcls-lattice. This is protected, only visible to members of the `slaclab` group.

This is mirrored at SLAC in `/afs`. To update the mirror:

```bash
cd /afs/slac/g/cd/swe/git/repos/model/lattice/lcls-lattice.git
git remote update
# (enter credentials)
```

On the production system, these are cloned at:
`/usr/local/lcls/model/lattice/lcls-lattice`

This is updated by:
```bash
git pull
```


