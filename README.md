# Sakai Installation Guide on WSL 20.04 (Ubuntu)

This guide provides step-by-step instructions to install JDK 11, Maven 3.8.4, Tomcat 9.0.78, and set up Sakai on Windows Subsystem for Linux (WSL) 20.04 (Ubuntu).

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Install JDK 11](#1-install-jdk-11)
- [2. Install Maven 3.8.4](#2-install-maven-384)
- [3. Set Up Tomcat Locally on Windows](#3-set-up-tomcat-locally-on-windows)
  - [3.1 Configure Environment Variables on WSL](#31-configure-environment-variables-on-wsl)
  - [3.2 Modify `server.xml` for International Character Support](#32-modify-serverxml-for-international-character-support)
  - [3.3 Create `setenv.bat`](#33-create-setenvbat)
  - [3.4 Improve Startup Speed](#34-improve-startup-speed)
- [4. Create a `sakai.properties` File](#4-create-a-sakaiproperties-file)
- [5. Set Up MySQL 8](#5-set-up-mysql-8)
  - [5.1 Extract JDBC Connector Jar into `tomcat/lib`](#51-extract-jdbc-connector-jar-into-tomcatlib)
- [6. Compile Sakai Source Code](#6-compile-sakai-source-code)
  - [6.1 Compile the Master Project](#61-compile-the-master-project)
  - [6.2 Build and Deploy Sakai](#62-build-and-deploy-sakai)
- [7. Start Up Sakai](#7-start-up-sakai)
- [Support](#support)
- [License](#license)

## Prerequisites

- **Operating System**: Windows 10 or later with WSL 2 enabled.
- **WSL Distribution**: Ubuntu 20.04.
- **Permissions**: Administrative privileges on both Windows and WSL.

## 1. Install JDK 11

Update your package list and install OpenJDK 11:

```bash
sudo apt update
sudo apt install openjdk-11-jdk -y
```

Verify the installation:

```bash
java -version
```

Set Env Vars on Ubuntu:

```bash
nano ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

## 2. Install Maven 3.8.4

Download and extract Maven:

```bash
wget https://archive.apache.org/dist/maven/maven-3/3.8.4/binaries/apache-maven-3.8.4-bin.tar.gz
sudo tar -xvzf apache-maven-3.8.4-bin.tar.gz -C /opt
sudo mv /opt/apache-maven-3.8.4 /opt/maven
```

Set up Maven environment variables:

```bash
echo "export MAVEN_HOME=/opt/maven" | sudo tee -a /etc/profile.d/maven.sh
echo "export PATH=\$MAVEN_HOME/bin:\$PATH" | sudo tee -a /etc/profile.d/maven.sh
echo "export MAVEN_OPTS='-Xms512m -Xmx1024m'" | sudo tee -a /etc/profile.d/maven.sh
sudo chmod +x /etc/profile.d/maven.sh
source /etc/profile.d/maven.sh
```

Verify Maven installation:

```bash
mvn -version
```

## 3. Set Up Tomcat Locally on Windows

Download and install Tomcat 9.0.78 on Windows:

- **Download Link**: [apache-tomcat-9.0.78.zip](https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.78/bin/apache-tomcat-9.0.78.zip)

```bash
wget https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.78/bin/apache-tomcat-9.0.78.tar.gz
sudo tar -xvzf apache-tomcat-9.0.78.tar.gz -C /opt
sudo mv /opt/apache-tomcat-9.0.78 /opt/tomcat
```

Extract it to `C:\tomcat`.

### 3.1 Configure Environment Variables on WSL

Set the `CATALINA_HOME` environment variable in WSL:

```bash
nano ~/.bashrc
```

Add the following line at the end of the file:

```bash
export CATALINA_HOME=/mnt/c/tomcat
```

Reload the `.bashrc` file:

```bash
source ~/.bashrc
```

Verify the variable:

```bash
echo $CATALINA_HOME
```

for linux
```bash
sudo chmod -R 777 /opt/tomcat
```

### 3.2 Modify `server.xml` for International Character Support

Edit `conf/server.xml` in your Tomcat directory and add `URIEncoding="UTF-8"` to the `<Connector>` element:

```xml
<Connector port="8080" URIEncoding="UTF-8" protocol="HTTP/1.1" ...
```

### 3.3 Create `setenv.bat`

Create a file called `setenv.bat` in `%CATALINA_HOME%\bin` with the following content:

```bat
set JAVA_OPTS=-server -Xmx1028m -XX:MaxMetaspaceSize=512m -Dorg.apache.jasper.compiler.Parser.STRICT_QUOTE_ESCAPING=false -Djava.awt.headless=true -Dcom.sun.management.jmxremote -Dhttp.agent=Sakai -Djava.util.Arrays.useLegacyMergeSort=true -Dfile.encoding=UTF8 -Dsakai.demo=true
```

### 3.4 Improve Startup Speed

Edit `conf/context.xml` and add the following `<JarScanner>` block within the `<Context>` element:

```xml
<Context>
    <!-- Other configurations -->

    <JarScanner>
        <!-- This speeds up startup by reducing scanning -->
        <JarScanFilter defaultPluggabilityScan="false" />
    </JarScanner>
</Context>
```

## 4. Create a `sakai.properties` File

Create a `sakai` directory in your Tomcat home:

```bash
mkdir $CATALINA_HOME/sakai
```

Create a `sakai.properties` file:

```bash
nano $CATALINA_HOME/sakai/sakai.properties
```

Add the following content (replace credentials as needed):

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

## 5. Set Up MySQL 8

Download and install MySQL 8:

- **Installer**: [mysql-8.0.40-winx64.msi](https://downloads.mysql.com/archives/installer/)

Create the Sakai database and user:

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

### 5.1 Extract JDBC Connector Jar into `tomcat/lib`

Download the MySQL JDBC Connector:

- [mysql-connector-j-8.0.32.zip](https://dev.mysql.com/downloads/connector/j/)

Extract the `mysql-connector-java-8.0.32.jar` file and place it into:

- **Windows**: `C:\tomcat\lib`
- **WSL**: `/mnt/c/tomcat/lib`

```bash
wget https://cdn.mysql.com/archives/mysql-connector-java-8.0/mysql-connector-j-8.0.32.tar.gz -O /tmp/mysql-connector-j-8.0.32.tar.gz
tar -xvzf /tmp/mysql-connector-j-8.0.32.tar.gz -C /tmp
sudo cp /tmp/mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar /opt/tomcat/lib/
ls /opt/tomcat/lib | grep mysql-connector-java
```

## 6. Compile Sakai Source Code

Clone the Sakai repository:

```bash
git clone --branch 23.x --single-branch https://github.com/thakurankit99/sakai.git
cd sakai
git checkout 23.x
```

### 6.1 Compile the Master Project

```bash
cd master
mvn clean install
```

### 6.2 Build and Deploy Sakai

Navigate back to the root directory and build:

```bash
cd ..
mvn clean install sakai:deploy -Dmaven.tomcat.home=$CATALINA_HOME \
-Dsakai.home=$CATALINA_HOME/sakai \
-Djava.net.preferIPv4Stack=true \
-Dmaven.test.skip=true
-Dmaven.cleanup=true
```

## 7. Start Up Sakai

Navigate to the Tomcat `bin` directory and start the server.

### For Windows:

Open Command Prompt and run:

```bat
cd C:\tomcat\bin
startup.bat
```

### For Mac/Linux (including WSL):

```bash
cd $CATALINA_HOME/bin
./startup.sh
```

check logs on linux
```bash
 tail -f /opt/tomcat/logs/catalina.out
```

## Support

If you encounter issues during installation, please refer to the Sakai [documentation](https://www.sakaiproject.org/) or open an issue on the [Sakai GitHub repository](https://github.com/sakaiproject/sakai).

## License

This project is licensed under the terms of the Apache License 2.0. See [LICENSE](LICENSE) for more details.

---
