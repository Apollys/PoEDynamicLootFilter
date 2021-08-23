import subprocess

def main():
    subprocess.run(['python', 'backend_cli.py', 'import_downloaded_filter'], shell=True)

if __name__ == '__main__':
    main()
