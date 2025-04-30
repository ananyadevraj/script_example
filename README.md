# Master Client List Automation Script 
A script to automate master client list generation from multiple monthly client enrollment sheets across programs. 

<ul>
  <li>This repository includes the base script for the automated master client list generation, implemented on the backend of a Streamlit UI app.</li>
  <li> The user can upload many monthly sheets of clients engaged across various programs, and receive a clean, easily readable master client list.</li>
  <li>Includes a duplicate checker function to merge clients that appear on multiple sheets.</li>
  <li>Tracks program enrollment through one-hot encoding, and identifies clients who are 'Dually Enrolled' across two programs or more.</li>
</ul>

### Streamlit App Flow
<ol>
  <li>User uploads multiple monthly Excel sheets with client enrollment information across programs.</li>
  <li>Each sheet is mapped to an ID and a display name for analysis and master list generation.</li>
  <li>Client selected which month and year the data is from.</li>
  <li>Upon pressing the 'run' button, the automation script runs and generates the master client list while handling duplicates from the monthly sheets.</li>
  <li>Client can then download the master client list for their given month in the form of an Excel file with multiple sheets - a master list, and sub-master lists for enrollment across each bucket of programs.</li>
</ol>
<br />
Please note that the code has been reduced without specific program names and column names in order to protect the data and privacy of the project. 
