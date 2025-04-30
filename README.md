# Master Client List Automation Script 
<strong>A script to automate master client list generation from multiple monthly client enrollment sheets across programs, implemented on the backend of a Streamlit UI app. </strong>

<ul>  `automating_master_client_list_generation.py`
  <li> The user can upload many monthly sheets of clients engaged across various programs, and receive an easily readable master client list.</li>
  <li> Cleans each monthly sheet and prepares it for processing to merge with all other sheets.</li>
  <li>Automatically creates one-hot encoding columns to track client activity across each program. </li>
  <li>Includes a duplicate checker function to merge clients that appear on multiple sheets and update their data accordingly.</li>
  <li>Identifies clients who are 'Dually Enrolled' across two programs or more based on the created one-hot encoded columns.</li>
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
