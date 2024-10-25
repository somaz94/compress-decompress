import os
import subprocess
import sys

def run_command(command):
    print(f"Executing command: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.stdout:
        print(f"Command output: {result.stdout.strip()}")
    if result.stderr:
        print(f"Command errors: {result.stderr.strip()}")

def get_extension(format):
    return {"zip": ".zip", "tar": ".tar", "tgz": ".tgz", "tbz2": ".tbz2"}.get(format, "")

def adjust_path(path):
    adjusted_path = (path if os.path.isabs(path) else os.path.join(os.getenv("GITHUB_WORKSPACE", os.getcwd()), path))
    print(f"Adjusted path: {adjusted_path}")
    return adjusted_path

def compress(source, format, include_root):
    source = adjust_path(source)

    # If the source is a file, we do not need to change the directory.
    if not os.path.isdir(source):
        sys.exit(f"Source {source} is not a directory, but a file. Ensure the source is a directory.")

    cwd = os.getcwd()  # Save current directory
    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)
        
    base_name = os.path.basename(source)
    extension = get_extension(format)
    full_dest = os.path.join(dest, f"{base_name}{extension}")
    
    print(f"Attempting to compress {source} to {full_dest}")
    
    # Zip format
    if format == "zip":
        if include_root == 'true':
            run_command(f"cd {os.path.dirname(source)} && zip -r {full_dest} {base_name}")
        else:
            run_command(f"cd {source} && zip -r {full_dest} *")
    
    # Tar format
    elif format == "tar":
        if include_root == 'true':
            run_command(f"tar -cvf {full_dest} -C {os.path.dirname(source)} {base_name}")
        else:
            run_command(f"tar -C {source} -cvf {full_dest} .")
    
    # Tgz format
    elif format == "tgz":
        if include_root == 'true':
            run_command(f"tar -czvf {full_dest} -C {os.path.dirname(source)} {base_name}")
        else:
            run_command(f"tar -C {source} -czvf {full_dest} .")
    
    # Tbz2 format
    elif format == "tbz2":
        if include_root == 'true':
            run_command(f"tar -cjvf {full_dest} -C {os.path.dirname(source)} {base_name}")
        else:
            run_command(f"tar -C {source} -cjvf {full_dest} .")
    
    else:
        sys.exit(f"Unsupported format: {format}")
    
    os.chdir(cwd)  # Restore original working directory.
    print(f"file_path={full_dest}", file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"))

def decompress(source, format):
    source = adjust_path(source)
    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)
    
    print(f"Attempting to decompress {source} to {dest if dest else 'current directory'}")
    
    if format == "zip":
        unzip_options = f"-d {dest}" if dest else "-j -d ."
        run_command(f"unzip {unzip_options} {source}")
    
    elif format == "tar":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar --absolute-names -xvf {source} {tar_options}")
    
    elif format == "tgz":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xzvf {source} {tar_options}")
    
    elif format == "tbz2":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xjvf {source} {tar_options}")
    
    else:
        sys.exit(f"Unsupported format: {format}")
    
    print(f"file_path={dest if dest else 'current directory'}", file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"))

if __name__ == "__main__":
    command = os.getenv("COMMAND")
    source = os.getenv("SOURCE")
    format = os.getenv("FORMAT")
    include_root = os.getenv("INCLUDEROOT", "false")  # default to false if not set

    if command == "compress":
        compress(source, format, include_root)
    elif command == "decompress":
        decompress(source, format)