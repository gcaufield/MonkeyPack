# MonkeyPack

A github release driven Package Manager for Connect IQ barrels

# Usage

`$ mbget`

## Basics

### Application Repository Configuration

The tool expects to find various files in the repository to determine where to
get dependancies from. The only non-standard ConnectIQ project file introduced is a
package map file (packages.txt)

```txt
project_root/
|-manifest.xml
|-packages.txt
```

#### Manifest File

No changes are required from the standard barrel dependency declarations that
are required for barrels to be included in a project, but they are called out
here to provide context for the package map file.

```xml
<iq:manifest xmlns:iq="http://www.garmin.com/xml/connectiq" version="3">
    <iq:application>
        <iq:products />
        <iq:permissions />
        <iq:languages />
        <iq:barrels>
            <iq:depends name="LibraryA" version="0.3.0"/>
            <iq:depends name="LibraryB" version="1.0.0"/>
        </iq:barrels>
    </iq:application>
</iq:manifest>
```

#### Package Map File

The package map file is a text file that is used to map `manifest.xml`
dependencies onto github repositories that the dependancy can be retrieved
from.

```txt
LibraryA=>GitHubLibraryARepo
LibraryB=>GitHubLibraryBRepo
```

### Library Repository Requirements

The tool expects that the libraries it downloads will make a new "Release" when
a version is available. The library should use semantic versions when tagging
releases.

The library must also include the barrel file in the release assets

