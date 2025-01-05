# Part A: Sakai Installation Guide on **Windows + WSL (Ubuntu 20.04)**

## Table of Contents
1. [Prerequisites](#prerequisites-wsl)  
2. [Install JDK 11](#1-install-jdk-11-wsl)  
3. [Install Maven 3.8.4](#2-install-maven-384-wsl)  
4. [Set Up Tomcat Locally on Windows (Using WSL)](#3-set-up-tomcat-windowswsl)  
   - [3.1 Configure Environment Variables on WSL](#31-configure-environment-variables-on-wsl)  
   - [3.2 Modify server.xml for International Character Support](#32-modify-serverxml-for-international-character-support-wsl)  
   - [3.3 Create setenv.bat](#33-create-setenvbat-wsl)  
   - [3.4 Improve Startup Speed](#34-improve-startup-speed-wsl)  
5. [Create a sakai.properties File](#4-create-a-sakaiproperties-file-wsl)  
6. [Set Up MySQL 8](#5-set-up-mysql-8-wsl)  
   - [5.1 Extract JDBC Connector Jar into tomcat/lib](#51-extract-jdbc-connector-jar-into-tomcatlib-wsl)  
7. [Compile Sakai Source Code](#6-compile-sakai-source-code-wsl)  
   - [6.1 Compile the Master Project](#61-compile-the-master-project-wsl)  
   - [6.2 Build and Deploy Sakai](#62-build-and-deploy-sakai-wsl)  
8. [Start Up Sakai](#7-start-up-sakai-wsl)  
9. [Support](#support-wsl)  
10. [License](#license-wsl)

---

## Prerequisites (WSL)
- **Operating System**: Windows 10 or later with WSL 2 enabled.
- **WSL Distribution**: Ubuntu 20.04 installed on Windows.
- **Permissions**: Administrative privileges on both Windows and WSL.

> **Important**:  
> 1. Avoid installing Tomcat **inside** WSL for this tutorial if you plan to use the Windows version of Tomcat. Mixing them can cause permission conflicts.  
> 2. Always confirm you’re using **Java 11** specifically, as using Java 17 or 8 can break Sakai 23.

---

## 1. Install JDK 11 (WSL)

Update your package list and install **OpenJDK 11** in your WSL Ubuntu 20.04 environment:

```bash
sudo apt update
sudo apt install openjdk-11-jdk -y
```

Set environment variables in WSL:

```bash
nano ~/.bashrc

# Add the following lines at the end:
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Save the file, then reload:
source ~/.bashrc
```

Verify the installation:

```bash
java -version
```

> **Tip**: If you see Java 8 or 17, remove or update them before installing Java 11 to avoid confusion.

---

## 2. Install Maven 3.8.4 (WSL)

Download and extract Maven 3.8.4:

```bash
wget https://archive.apache.org/dist/maven/maven-3/3.8.4/binaries/apache-maven-3.8.4-bin.tar.gz
sudo tar -xvzf apache-maven-3.8.4-bin.tar.gz -C /opt
sudo mv /opt/apache-maven-3.8.4 /opt/maven
```

Set up Maven environment variables in WSL:

```bash
nano ~/.bashrc

# Add the following lines at the end:
export MAVEN_HOME=/opt/maven
export PATH=$MAVEN_HOME/bin:$PATH

# Save, then reload:
source ~/.bashrc
```

Verify Maven installation:

```bash
mvn -version
```

> **Note**: Confirm Maven is actually using Java 11 by checking the output of `mvn -version`.

---

## 3. Set Up Tomcat Locally on **Windows** (Using WSL)

### 3.1 Configure Environment Variables on WSL

1. **Download Tomcat 9.0.78 (Windows binary)**:
   - [apache-tomcat-9.0.78.zip](https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.78/bin/apache-tomcat-9.0.78.zip)
   - Extract it to `C:\tomcat`

2. In WSL, set `CATALINA_HOME` to point to the Windows folder:

   ```bash
   nano ~/.bashrc
   
   # Add:
   export CATALINA_HOME=/mnt/c/tomcat

   # Reload and verify:
   source ~/.bashrc
   echo $CATALINA_HOME
   ```

> **Caution**: Ensure there are **no spaces** in your Tomcat path (e.g., avoid `C:\Program Files\tomcat`). Spaces often break classpath references in Windows and WSL.

---

### 3.2 Modify server.xml for International Character Support (WSL)

In Windows, open `C:\tomcat\conf\server.xml` in a text editor and add `URIEncoding="UTF-8"` to the `<Connector>` element:

```xml
<Connector port="8080" URIEncoding="UTF-8" protocol="HTTP/1.1" ...
```

---

### 3.3 Create setenv.bat (WSL / Windows)

Create a file called **setenv.bat** in **`%CATALINA_HOME%\bin`** (i.e., `C:\tomcat\bin\setenv.bat`) with the following content:

```bat
set JAVA_OPTS=-server -Xmx1028m -XX:MaxMetaspaceSize=512m -Dorg.apache.jasper.compiler.Parser.STRICT_QUOTE_ESCAPING=false -Djava.awt.headless=true -Dcom.sun.management.jmxremote -Dhttp.agent=Sakai -Djava.util.Arrays.useLegacyMergeSort=true -Dfile.encoding=UTF8 -Dsakai.demo=true
```

> **Note**:  
> - This file is specific to **Windows** Tomcat usage.  
> - Keep an eye on memory settings (`-Xmx1028m`); you may need a larger heap if you have many users or large content.  
> - `-Dsakai.demo=true` will **populate** a demo database on first startup. Remove that flag once you’ve got your test data.

---

### 3.4 Improve Startup Speed (WSL)

In `C:\tomcat\conf\context.xml`, add the following `<JarScanner>` block within the `<Context>` element:

```xml
<Context>
    <!-- Other configurations -->

    <JarScanner>
        <!-- This speeds up startup by reducing scanning -->
        <JarScanFilter defaultPluggabilityScan="false" />
    </JarScanner>
</Context>
```

---

## 4. Create a sakai.properties File (WSL)

Create a `sakai` directory under your Tomcat home on **Windows**:

```bash
mkdir /mnt/c/tomcat/sakai
```

Create/edit the **sakai.properties**:

```bash
nano /mnt/c/tomcat/sakai/sakai.properties
```

Add the following (adjust credentials as needed):

```properties
username@javax.sql.BaseDataSource=aadyatech
password@javax.sql.BaseDataSource=1234

## MySQL settings
vendor@org.sakaiproject.db.api.SqlService=mysql
driverClassName@javax.sql.BaseDataSource=com.mysql.jdbc.Driver
hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
url@javax.sql.BaseDataSource=jdbc:mysql://127.0.0.1:3306/sakai?useUnicode=true&characterEncoding=UTF-8
validationQuery@javax.sql.BaseDataSource=
defaultTransactionIsolationString@javax.sql.BaseDataSource=TRANSACTION_READ_COMMITTED
```

> **Note**: If you store `sakai.properties` outside of `C:\tomcat`, be sure to set `-Dsakai.home` in your Tomcat startup (`setenv.bat`) to point to that directory.

---

## 5. Set Up MySQL 8 (WSL)

You can install MySQL 8 **natively on Windows** using the installer, or within WSL itself. Many find it simpler to run MySQL on Windows for performance and separate resource usage, but both approaches work.

- **MySQL Installer** (Windows): [mysql-8.0.40-winx64.msi](https://downloads.mysql.com/archives/installer/)

Create the Sakai database and user (run these in MySQL CLI or a GUI like MySQL Workbench):

```sql
mysql -u root -p

CREATE DATABASE sakai DEFAULT CHARACTER SET utf8;
CREATE USER 'aadyatech'@'localhost' IDENTIFIED BY '1234';
GRANT ALL ON sakai.* TO 'aadyatech'@'localhost';

CREATE USER 'aadyatech'@'127.0.0.1' IDENTIFIED BY '1234';
GRANT ALL ON sakai.* TO 'aadyatech'@'127.0.0.1';

FLUSH PRIVILEGES;
QUIT;
```

> **Note**: Use a stronger password in production environments.

### 5.1 Extract JDBC Connector Jar into tomcat/lib (WSL)

Download the MySQL JDBC Connector in **Windows** or WSL:

- [mysql-connector-j-8.0.32.zip](https://dev.mysql.com/downloads/connector/j/)

Extract the **`mysql-connector-java-8.0.32.jar`** file and place it into `C:\tomcat\lib`.

---

## 6. Compile Sakai Source Code (WSL)

Clone the Sakai repository **inside WSL**:

```bash
git clone --branch 23.x --single-branch https://github.com/thakurankit99/sakai.git
cd sakai
git checkout 23.x
```

> **Note**: Avoid storing the code on a Windows-mounted drive (`/mnt/c`) if you plan to do a lot of file operations in WSL, as file I/O can be slower. However, for a small-scale dev environment, it’s usually fine.

---

### 6.1 Compile the Master Project (WSL)

```bash
cd master
mvn clean install
```

---

### 6.2 Build and Deploy Sakai (WSL)

Go back to the root of the Sakai project and run:

```bash
cd ..
mvn clean install sakai:deploy \
  -Dmaven.tomcat.home=$CATALINA_HOME \
  -Dsakai.home=$CATALINA_HOME/sakai \
  -Djava.net.preferIPv4Stack=true \
  -Dmaven.test.skip=true \
  -Dmaven.cleanup=true
```

> **Important**:  
> - `-Dmaven.tomcat.home=$CATALINA_HOME` ensures the code deploys into `C:\tomcat\` (which appears as `/mnt/c/tomcat` in WSL).  
> - `-Dsakai.home=$CATALINA_HOME/sakai` references the same folder for your `sakai.properties`.  
> - `-Dmaven.test.skip=true` speeds up builds by skipping tests but can hide potential problems.

---

## 7. Start Up Sakai (WSL)

From **Windows**, open a Command Prompt and start Tomcat:

```bat
cd C:\tomcat\bin
startup.bat
```

Or from **WSL** (navigating via `/mnt/c/`):

```bash
cd /mnt/c/tomcat/bin
./startup.bat
```

> **Note**: `.bat` scripts run under Windows’ CMD/PowerShell. If you prefer to manage Tomcat entirely in WSL, you should install a **Linux** version of Tomcat under `/opt/tomcat` in your WSL filesystem. (See **Part B**.)

Check logs (in WSL, tail the log in Windows folder):

```bash
tail -f /mnt/c/tomcat/logs/catalina.out
```

> **Tip**: If you see errors about “Port 8080 already in use,” make sure no other process (like Windows IIS or another Tomcat) is running on port 8080.

---

## Support (WSL)

If you encounter issues during installation, please refer to the [Sakai documentation](https://www.sakaiproject.org/) or open an issue on the [Sakai GitHub repository](https://github.com/sakaiproject/sakai).

- Common WSL pitfalls:
  - File permissions not matching between Windows and WSL.
  - Mixed line endings in `.sh` or `.bat` scripts.
  - Conflicting Java versions in Windows vs. WSL.

---

## License (WSL)

This project is licensed under the terms of the Apache License 2.0. See [LICENSE](LICENSE) for more details.

---

# Part B: Sakai Installation Guide on **Native Linux (Ubuntu 20.04)**

## Table of Contents
1. [Prerequisites](#prerequisites-linux)  
2. [Install JDK 11](#1-install-jdk-11-linux)  
3. [Install Maven 3.8.4](#2-install-maven-384-linux)  
4. [Set Up Tomcat on Linux](#3-set-up-tomcat-linux)  
   - [3.1 Configure Environment Variables on Linux](#31-configure-environment-variables-on-linux)  
   - [3.2 Modify server.xml for International Character Support](#32-modify-serverxml-for-international-character-support-linux)  
   - [3.3 Create setenv.sh](#33-create-setenvsh-linux)  
   - [3.4 Improve Startup Speed](#34-improve-startup-speed-linux)  
5. [Create a sakai.properties File](#4-create-a-sakaiproperties-file-linux)  
6. [Set Up MySQL 8](#5-set-up-mysql-8-linux)  
   - [5.1 Extract JDBC Connector Jar into tomcat/lib](#51-extract-jdbc-connector-jar-into-tomcatlib-linux)  
7. [Compile Sakai Source Code](#6-compile-sakai-source-code-linux)  
   - [6.1 Compile the Master Project](#61-compile-the-master-project-linux)  
   - [6.2 Build and Deploy Sakai](#62-build-and-deploy-sakai-linux)  
8. [Start Up Sakai](#7-start-up-sakai-linux)  
9. [Support](#support-linux)  
10. [License](#license-linux)

---

## Prerequisites (Linux)
- **Operating System**: Ubuntu 20.04 (native install).
- **Permissions**: Administrative (sudo) privileges.

---

## 1. Install JDK 11 (Linux)

```bash
wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.16.1%2B1/OpenJDK11U-jdk_x64_linux_hotspot_11.0.16.1_1.tar.gz -O /tmp/temurin11.tar.gz
sudo tar -xvzf /tmp/temurin11.tar.gz -C /opt
sudo mv /opt/jdk-11.0.16.1+1 /opt/temurin-11
```

Set environment variables:

```bash
nano ~/.bashrc

# Add:
export JAVA_HOME=/opt/temurin-11
export PATH=$JAVA_HOME/bin:$PATH

source ~/.bashrc
```

Verify:

```bash
java -version
```

---

## 2. Install Maven 3.8.4 (Linux)

```bash
wget https://archive.apache.org/dist/maven/maven-3/3.8.4/binaries/apache-maven-3.8.4-bin.tar.gz
sudo tar -xvzf apache-maven-3.8.4-bin.tar.gz -C /opt
sudo mv /opt/apache-maven-3.8.4 /opt/maven
```

Update environment variables:

```bash
nano ~/.bashrc

# Add:
export MAVEN_HOME=/opt/maven
export PATH=$MAVEN_HOME/bin:$PATH
export MAVEN_OPTS='-Xms512m -Xmx1024m'

source ~/.bashrc
mvn -version
```

---

## 3. Set Up Tomcat on Linux

### 3.1 Configure Environment Variables on Linux

1. Download Tomcat 9.0.78:
   ```bash
   wget https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.78/bin/apache-tomcat-9.0.78.tar.gz
   sudo tar -xvzf apache-tomcat-9.0.78.tar.gz -C /opt
   sudo mv /opt/apache-tomcat-9.0.78 /opt/tomcat
   ```

2. Set `CATALINA_HOME`:
   ```bash
   nano ~/.bashrc
   export CATALINA_HOME=/opt/tomcat
   source ~/.bashrc
   echo $CATALINA_HOME
   ```

3. Adjust permissions so Tomcat can be managed easily:
   ```bash
   sudo chmod -R 777 /opt/tomcat
   ```
   > **Note**: `chmod -R 777` is **insecure** for production. For development, it’s okay, but in production use a more restrictive approach (e.g., `chown -R tomcat:tomcat /opt/tomcat` and `chmod 755`).

---

### 3.2 Modify server.xml for International Character Support (Linux)

Edit `/opt/tomcat/conf/server.xml`:

```xml
<Connector port="8080" URIEncoding="UTF-8" protocol="HTTP/1.1" ...
```

---

### 3.3 Create setenv.sh (Linux)

Create a file called **`setenv.sh`** in `/opt/tomcat/bin/`:

```bash
nano /opt/tomcat/bin/setenv.sh
```

Add the following (example):

```bash
export JAVA_OPTS="-Xms2g -Xmx2g -Djava.awt.headless=true"
JAVA_OPTS="$JAVA_OPTS -Dhttp.agent=Sakai"
JAVA_OPTS="$JAVA_OPTS -Dorg.apache.jasper.compiler.Parser.STRICT_QUOTE_ESCAPING=false"
JAVA_OPTS="$JAVA_OPTS -Duser.timezone=US/Eastern"
JAVA_OPTS="$JAVA_OPTS -Dsakai.cookieName=SAKAI2SESSIONID"
JAVA_OPTS="$JAVA_OPTS -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=8089 -Dcom.sun.management.jmxremote.local.only=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"
JAVA_OPTS="$JAVA_OPTS \
  --add-exports=java.base/jdk.internal.misc=ALL-UNNAMED \
  --add-exports=java.base/sun.nio.ch=ALL-UNNAMED \
  --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED \
  --add-exports=jdk.internal.jvmstat/sun.jvmstat.monitor=ALL-UNNAMED \
  --add-exports=java.base/sun.reflect.generics.reflectiveObjects=ALL-UNNAMED \
  --add-opens=jdk.management/com.sun.management.internal=ALL-UNNAMED \
  --illegal-access=permit"
```

Make it executable:

```bash
chmod +x /opt/tomcat/bin/setenv.sh
```

---

### 3.4 Improve Startup Speed (Linux)

In `/opt/tomcat/conf/context.xml`, add:

```xml
<Context>
    <!-- Other configurations -->

    <JarScanner>
        <JarScanFilter defaultPluggabilityScan="false" />
    </JarScanner>
</Context>
```

---

## 4. Create a sakai.properties File (Linux)

```bash
mkdir /opt/tomcat/sakai
nano /opt/tomcat/sakai/sakai.properties
```

Example config:

```properties
username@javax.sql.BaseDataSource=aadyatech
password@javax.sql.BaseDataSource=1234

## MySQL settings
vendor@org.sakaiproject.db.api.SqlService=mysql
driverClassName@javax.sql.BaseDataSource=com.mysql.jdbc.Driver
hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
url@javax.sql.BaseDataSource=jdbc:mysql://127.0.0.1:3306/sakai?useUnicode=true&characterEncoding=UTF-8
validationQuery@javax.sql.BaseDataSource=
defaultTransactionIsolationString@javax.sql.BaseDataSource=TRANSACTION_READ_COMMITTED
```

---

## 5. Set Up MySQL 8 (Linux)

Install MySQL server on Ubuntu:

```bash
sudo apt update
sudo apt install mysql-server -y
```

Secure the installation and set root password (optional):

```bash
sudo mysql_secure_installation
```

Create the Sakai database and user:

```bash
mysql -u root -p

CREATE DATABASE sakai DEFAULT CHARACTER SET utf8;
CREATE USER 'aadyatech'@'localhost' IDENTIFIED BY '1234';
GRANT ALL ON sakai.* TO 'aadyatech'@'localhost';

CREATE USER 'aadyatech'@'127.0.0.1' IDENTIFIED BY '1234';
GRANT ALL ON sakai.* TO 'aadyatech'@'127.0.0.1';

FLUSH PRIVILEGES;
QUIT;
```

---

### 5.1 Extract JDBC Connector Jar into tomcat/lib (Linux)

```bash
wget https://cdn.mysql.com/archives/mysql-connector-java-8.0/mysql-connector-j-8.0.32.tar.gz -O /tmp/mysql-connector-j-8.0.32.tar.gz
tar -xvzf /tmp/mysql-connector-j-8.0.32.tar.gz -C /tmp
sudo cp /tmp/mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar /opt/tomcat/lib/
ls /opt/tomcat/lib | grep mysql-connector-java
```

---

## 6. Compile Sakai Source Code (Linux)

```bash
git clone --branch 23.x --single-branch https://github.com/thakurankit99/sakai.git
cd sakai
git checkout 23.x
```

### 6.1 Compile the Master Project (Linux)

```bash
cd master
mvn clean install
```

### 6.2 Build and Deploy Sakai (Linux)

```bash
cd ..
mvn clean install sakai:deploy \
  -Dmaven.tomcat.home=$CATALINA_HOME \
  -Dsakai.home=$CATALINA_HOME/sakai \
  -Djava.net.preferIPv4Stack=true \
  -Dmaven.test.skip=true \
  -Dmaven.cleanup=true
```

---

## 7. Start Up Sakai (Linux)

```bash
cd $CATALINA_HOME/bin
./startup.sh
```

Check logs:

```bash
tail -f /opt/tomcat/logs/catalina.out
```

---

## Support (Linux)

For issues, refer to the [Sakai documentation](https://www.sakaiproject.org/) or open an issue on the [Sakai GitHub repository](https://github.com/sakaiproject/sakai).

---

## License (Linux)

This project is licensed under the terms of the Apache License 2.0. See [LICENSE](LICENSE) for more details.

---

**Enjoy your Sakai 23 installation on both Windows + WSL and native Ubuntu!**
