# *Create separate repo for separate packages*

Should we create use a single repository or create separate repositories to hold re-usable packages (SDKs, libraries, etc) that we will create as part of microservice.py 

## Considered Alternatives

* Single repo
* Separate repo

## Decision Outcome

* Chosen Alternative: Create separate repos

## Pros and Cons of the Alternatives <!-- optional -->

### Single repo

* `+` Single place to find everything
* `-` CI might take a while to run when we have tons of packages

### Separate repo

* `+` Each repo is now standable
* `-` Find a place to create an index of sorts to list all the packages
