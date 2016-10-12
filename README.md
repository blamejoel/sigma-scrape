## sigma-scrape

#### Dependencies
python3
selenium
beautifulsoup4
Google Chrome/Chromium

### Prep
Compile a list of CAS numbers to downloads SDS sheets for, with each CAS number 
on a new line.

### Using chem-scrape
Run `python3 sigma-scrape.py`, sigma-scrape will parse through the CAS-list.txt 
file and attempt to download the SDS sheet corresponding to each CAS number.

An error will be reported at the end if the download was not successful.

### Known Issues
Work in progress...

### Feedback
Star this repo if you found it useful. Use the github issue tracker to give
feedback on this repo.

## Licensing
See [LICENSE](LICENSE)

## Author
Joel Gomez

## Credits
Based on the work by [arnauddevie]
(https://github.com/arnauddevie/Hazard-Assessment-CAS-Lookup).
