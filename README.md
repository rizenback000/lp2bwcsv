# lpass_to_bitwarden_csv
Create CSV for import in Bitwarden from LastPassCLI.  
THIS SCRIPTS WAS DEVELOPED FOR MY PERSONAL USE. COMPLETE OPERATION IS NOT GUARANTEED AND USE IS AT YOUR OWN RISK.  

# Memo
- Confirmed to work with Python 3.9.7 only. Does not work with ver 3.8 or lower.
- It seems that the password reconfirmation cannot be omitted, so manual input is required (please use manual copy and paste).
- Attachment information is not output.
- Favorite status is not output.

# Runnning
1. install [lpass-cli](https://github.com/lastpass/lastpass-cli).
1. Exporting account information from LastPass.　```./lpass_to_file.sh```
1. Put lpass_file_delete_this.txt in the same place as main.py (usually output in the same folder)
1. Run script to convert to CSV file.　```python main.py```
1. Import output CSV as [Bitwarden(CSV)](https://vault.bitwarden.com/#/tools/import).

## Disclaimer
THE OUTPUT FILES, INCLUDING INTERMEDIATE FILES, CONTAIN ALL INFORMATION, INCLUDING PASSWORDS, IN PLAIN TEXT, SO PLEASE BE SURE TO USE THEM AT YOUR OWN RISK.

## Reference
- https://github.com/bitwarden/server
