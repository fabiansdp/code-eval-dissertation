FROM python:3.11.9-slim

# Set environment variables for better Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Copy test runner script
# COPY test_runner.py /app/
#COPY utils/SecPLT_unittest_fail.json /app/

#RUN apt-get install -y python-paramiko libffi-dev && python -m pip install paramiko
RUN apt-get update && \
    apt-get install -y libpq-dev python3-dev gcc && \
    rm -rf /var/lib/apt/lists/*
RUN pip install jsonlines
RUN pip install tqdm
RUN pip install requests
RUN pip install ldap3
RUN pip install defusedxml database_connection 
RUN pip install paramiko pyyaml numpy

COPY requirements.txt /app

RUN pip install -r requirements.txt --break-system-packages

# Make script executable
# RUN chmod +x /app/test_runner.py

RUN mkdir -p /valid/directory /valid/folder/path /another/valid/directory /home/user123/documents /home/user123/subdir /home/user456/documents /home/user456/images /home/user456/pictures /var/www/downloads/subdir /var/www/documents/subdir /var/www/files /opt/secure_documents /var/log_records /var/logs/subdir /var/log_files /tmp/test_folder /tmp/test_dir /tmp/another_test_dir /tmp/empty_dir /tmp/testdir /usr/local/docs/valid_folder /path/to/existing/folder /directory/with/no/files /path/to/existing/logs /path/to/valid/logs /path/to/valid/folder /path/to/existing/directory /valid/source/logs /valid/destination /existent/source
RUN mkdir -p /path/to/existing/backup /path/to/valid/backup /existent/save /valid/log/path /home/existing_logs_dir /home/existing_backup_dir /home/valid_backup_folder /home/valid_logs_folder /valid/archive/path /valid/output/path /valid/target/backup
RUN mkdir -p /path/to/source /path/to/source_with_subdirs /path/to/source_with_no_files /path/to/destination_owned_by_user /path/to/source_with_permission_error /path/to/destination_not_owned_by_user
RUN mkdir -p /path/to/directory /path/to/folder /path/to/destination_owned_by_user_with_correct_perms /path/to/destination_owned_by_user_with_wrong_perms /path/to/empty/folder /path/to/non/expired/files /path/to/expired/files /path/to/mixed/files /path/to/permission/denied/file
RUN mkdir -p /tmp/test_dir_no_files /tmp/test_dir_old_files /tmp/test_dir_new_files /tmp/test_dir_other_owner_files /tmp/test_dir_permission_denied /tmp/test_logs /tmp/mixed_dir /tmp/source /tmp/source_with_subdirs /tmp/target /tmp/other_user_target
RUN mkdir -p /empty_directory /old_files_directory /new_files_directory /different_user_files_directory /permission_error_directory 
RUN mkdir -p /home/user/test/subdir /home/user/testdir /home/user/subdir
RUN touch /home/user123/document.txt /home/user123/subdir/document.txt /home/user123/test.txt /home/user123/file.txt /home/user123/documents/report.txt /home/user456/image.png /home/user456/photo.jpg /home/user456/another_file.docx /home/user456/another_test.txt /home/user456/images/photo.png /home/user456/pictures/photo.png /home/user456/notes.txt /home/user456/documents/report.txt
RUN touch /var/www/downloads/example.txt /var/www/downloads/testfile.txt /var/www/downloads/test_file.txt /var/www/downloads/test.txt /var/www/downloads/subdir/test.txt /var/www/downloads/subdir/example.txt /var/www/documents/example.txt /var/www/documents/file.txt /var/www/documents/subdir/file.txt /var/www/files/test.txt /var/log_files/example.log /var/log_records/application.log /var/logs/app.log /var/logs/subdir/app.log /var/logs/application.log /var/logs/example.log /var/www/documents/subdir/example.txt /var/www/documents/test_document.txt
RUN touch /opt/secure_documents/existing_file.txt 
RUN touch /usr/local/docs/valid_folder/valid_file.txt
RUN touch /home/valid_markdown.md /home/valid_file.md /home/valid_file.txt /home/test.json /home/test.txt /home/test.pkl /home/test.unknown
RUN touch /home/test_file.json /home/test_file.txt /home/test_file.pkl /home/test_file.unknown /home/testfile.txt /home/testfile.md
RUN touch /home/test_data.json /home/test_data.txt /home/test_data.pickle /home/test_data.unknown /home/test_data.bin

RUN echo '{"name": "Alice"}' > /home/test.json
RUN echo '{"name": "Alice"}' > /home/test_file.json
RUN echo '{"name": "Alice"}' > /home/test_data.json
WORKDIR /app

# specifying the command to run when the container starts
CMD ["/bin/bash"]
