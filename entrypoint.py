import os
import subprocess
import sys

def run_command(command):
    print(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        if result.stdout:
            print(f"Command output: {result.stdout.strip()}")
        if result.stderr:
            print(f"Command errors: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")

def get_extension(format):
    return {
        'zip': '.zip',
        'tar': '.tar',
        'tgz': '.tgz',
        'tbz2': '.tbz2'
    }.get(format, '')

def adjust_path(path):
    if not path:
        raise ValueError("Source path is not provided or is None.")
    adjusted_path = path if os.path.isabs(path) else os.path.join(os.getenv('GITHUB_WORKSPACE', os.getcwd()), path)
    print(f"Adjusted path: {adjusted_path}") 
    return adjusted_path

def compress(source, format):
    source = adjust_path(source)
    cwd = os.getcwd()  # Save current directory
    os.chdir(os.path.dirname(source))  # Change to directory of the source

    dest = os.getenv('DEST', os.getenv('GITHUB_WORKSPACE', os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)
    base_name = os.path.basename(source)
    extension = get_extension(format)
    full_dest = os.path.join(dest, f"{base_name}{extension}")

    print(f"Attempting to compress {source} to {full_dest}")
    if format == 'zip':
        run_command(f'zip -r {full_dest} {base_name}')
    elif format == 'tar':
        run_command(f'tar --absolute-names -cvf {full_dest} {base_name}')
    elif format == 'tgz':
        run_command(f'tar -P -czvf {full_dest} {base_name}')
    elif format == 'tbz2':
        run_command(f'tar -P -cjvf {full_dest} {base_name}')
    else:
        sys.exit(f"Unsupported format: {format}")
    
    os.chdir(cwd)  # Restore original working directory
    print(f"file_path={full_dest}", file=open(os.getenv('GITHUB_OUTPUT', '/dev/stdout'), 'a'))
    return full_dest

def decompress(source, format):
    source = adjust_path(source)
    dest = os.getenv('DEST', os.getenv('GITHUB_WORKSPACE', os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)

    print(f"Attempting to decompress {source} to {dest if dest else 'current directory'}")
    if format == 'zip':
        unzip_options = f"-d {dest}" if dest else "-j -d ."
        run_command(f"unzip {unzip_options} {source}")
    elif format == 'tar':
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar --absolute-names -xvf {source} {tar_options}")
    elif format == 'tgz':
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xzvf {source} {tar_options}")
    elif format == 'tbz2':
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xjvf {source} {tar_options}")
    else:
        sys.exit(f"Unsupported format: {format}")

    print(f"file_path={dest if dest else 'current directory'}", file=open(os.getenv('GITHUB_OUTPUT', '/dev/stdout'), 'a'))
    return dest

def set_output(name, value):
    with open(os.getenv('GITHUB_OUTPUT', '/dev/stdout'), 'a') as f:
        f.write(f"{name}={value}\n")

if __name__ == "__main__":

    print("Received command:", os.getenv('command'))
    print("Received source:", os.getenv('source'))
    print("Received format:", os.getenv('format'))
    
    command = os.getenv('command')
    source = os.getenv('source')
    format = os.getenv('format')

    if not source:
        print("Error: The 'SOURCE' environment variable is not set.")
        sys.exit(1)

    file_path = compress(source, format) if command == 'compress' else decompress(source, format)
    set_output("file_path", file_path)