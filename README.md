PGInventoryManager
==================

The current version is hosted at pginventorymanager.appspot.com

Rows:
- Quantity is how many to order per week.
- UPC is the internal UPC we use for our system
- Pack Size is the # of each drink that comes in a pack (usually 6, 12, 24, etc)
- If you want to change the pack size or manually change the quantity, just change the relevant field and hit "Update"
- Hit Delete if you want to wipe that row off of the database.

Usage:
- Every UPC you enter into the box above "Scan UPC" will increment an internal estimation of how many units we need per week.  This will sometimes increase the "quantity" column.
- The box above "Input UPC" is used for bulk adding UPCs to the database.  The data has to be a CSV with the rows in the following order:
  1) Quantity
  2) Pack Size
  3) UPC
  4) Name
  5) image URL
  6) Vendor
- The "Delete All Data" button will do just that.
