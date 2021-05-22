call config.cmd
::création arborescence machine windows
mkdir %local_default_directory%\%folder_name_store_data%\data_in 
mkdir %local_default_directory%\%folder_name_store_data%\data_out

::copie des données du dossier contenant les fichiers à transférer dans le dossier du projet
xcopy /s %path_files_to_transfer_directory% %local_default_directory%\%folder_name_store_data%\data_in

::création de l'arborescence dans hdfs
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "hadoop fs -mkdir ./%folder_name_store_data%"

::copie des fichier de W10 --> hadoop
scp -P 2222 %local_default_directory%/%folder_name_store_data%/data_in/label.csv %username%@sandbox-hdp.hortonworks.com:/home/%username%/
scp -P 2222 %local_default_directory%/%folder_name_store_data%/data_in/data.json %username%@sandbox-hdp.hortonworks.com:/home/%username%/
scp -P 2222 %local_default_directory%/%folder_name_store_data%/data_in/categories_string.csv %username%@sandbox-hdp.hortonworks.com:/home/%username%/

::copie des fichier de hadoop --> hdfs
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "hadoop fs -copyFromLocal /home/%username%/label.csv ./%path_hdfs%/" 
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "hadoop fs -copyFromLocal /home/%username%/data.json ./%path_hdfs%/"
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "hadoop fs -copyFromLocal /home/%username%/categories_string.csv ./%path_hdfs%/"

::copie des fichiers de hdfs --> hadoop
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "hadoop fs -copyToLocal ./%path_hdfs%/label.csv /home/%username%/"
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "hadoop fs -copyToLocal ./%path_hdfs%/data.json /home/%username%/"
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "hadoop fs -copyToLocal ./%path_hdfs%/categories_string.csv /home/%username%/"

::copie des fichiers de hadoop --> W10
scp -P 2222 %username%@sandbox-hdp.hortonworks.com:/home/%username%/label.csv %local_default_directory%/%folder_name_store_data%/data_out/
scp -P 2222 %username%@sandbox-hdp.hortonworks.com:/home/%username%/data.json %local_default_directory%/%folder_name_store_data%/data_out/
scp -P 2222 %username%@sandbox-hdp.hortonworks.com:/home/%username%/categories_string.csv %local_default_directory%/%folder_name_store_data%/data_out/

::supression fichier hadoop
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "rm /home/%username%/label.csv" 
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "rm /home/%username%/data.json" 
plink -ssh -P 2222 -batch -pw %password% %username%@localhost "rm /home/%username%/categories_string.csv" 