# Apache Solr 9 Installation

This guide provides step-by-step instructions for installing Apache Solr 9 on your system.

## Prerequisites

Before you begin, make sure you meet the following prerequisites:

- **Java**: Apache Solr is a Java-based application. Ensure that you have Java 8 or higher installed and correctly configured on your system.

## Download Solr

1. Visit the official Apache Solr download page by navigating to [Apache Solr Downloads](https://lucene.apache.org/solr/downloads.html).

2. Choose the Solr version you want to install and download the appropriate binary distribution for your operating system. Select the "Binary Release" option.

## Extract the Solr Archive

3. Extract the downloaded Solr archive to your preferred installation directory. Use the following command as an example (replace `solr-9.x.x` with the actual version you downloaded):

   ```bash
   cd ~/
   tar zxf solr-9.3.0.tgz
   ```

   Replace `solr-9.3.0.tgz` with the path to your downloaded Solr archive.

## Start Solr

4. Change to the Solr installation directory:

   ```bash
   cd solr-9.3.0
   ```

5. Start Solr in standalone mode:

   - For Unix:

     ```bash
     bin/solr start
     ```

   - For Windows:

     ```bash
     bin\solr.cmd start
     ```

6. To verify that Solr is running, open a web browser and navigate to [http://localhost:8983/solr/](http://localhost:8983/solr/). You should see the Solr admin interface.

7. If you have changed the default Solr port and host, make sure to update those settings in your project's configuration files, such as `settings.py`.

# Moving a Solr Core File

This guide explains how to move a Solr core file from project directory to your Solr server directory. This step is necessary to make the Solr core available for indexing and querying.

## Steps to Move a Solr Core

1. **Determine Your Solr Server Directory**:

   - Determine the path to your Solr server directory where Solr cores are typically stored. This directory is commonly located at:
     - On Unix-based systems: `/path/to/solr/server/solr`
     - On Windows: `C:\path\to\solr\server\solr`

   Example: `/home/user/solr-9.3.0/server/solr`

2. **Copy the Solr Core**:

   - Copy the `documents_data` folder from project directory to the Solr server directory. You can use a file manager or command-line tools to do this.

3. **Verify the Core Transfer**:

   - Ensure that the Solr core directory is now located in the Solr server directory. You should see your core directory alongside other Solr cores.

4. **Restart Solr**:

   - Restart your Solr server to recognize the newly added Solr core. You can do this by running one of the following commands:
     - For Unix-based systems:
       ```bash
       bin/solr restart
       ```
     - For Windows:
       ```bash
       bin\solr.cmd restart
       ```

5. **Access the Core**:
   - After restarting Solr, you can access the newly added Solr core using its core name in the URL. The URL format typically follows this pattern:
     ```
     http://localhost:8983/solr/documents_data/
     ```

**Notes**:

- If you encounter permission issues when copying the core, make sure you have the necessary permissions to write to the Solr server directory.
