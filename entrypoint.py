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
    return {"zip": ".zip", "tar": ".tar", "tgz": ".tgz", "tbz2": ".tbz2"}.get(
        format, ""
    )


def adjust_path(path):
    adjusted_path = (
        path
        if os.path.isabs(path)
        else os.path.join(os.getenv("GITHUB_WORKSPACE", os.getcwd()), path)
    )
    print(f"Adjusted path: {adjusted_path}")
    return adjusted_path


def compress(source, format, include_root):
    source = adjust_path(source)
    cwd = os.getcwd()  # Save current directory
    print(f"Initial CWD: {cwd}")  # Debug: Show initial working directory

    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)

    base_name = os.path.basename(source)
    extension = get_extension(format)
    full_dest = os.path.join(dest, f"{base_name}{extension}")
    print(f"Destination Path: {full_dest}")  # Debug: Show full destination path

    if os.path.isdir(source):
        # Compress a directory with the option of including root
        print(f"Attempting to compress directory {source} to {full_dest}")
        if include_root == "true":
            compress_target = base_name
            os.chdir(os.path.dirname(source))  # Change to directory of the source
        else:
            compress_target = "."
            os.chdir(
                source
            )  # Change to the source directory itself to compress its contents
        print(
            f"Changed CWD for Compression: {os.getcwd()}"
        )  # Debug: Show CWD for compression
    else:
        # Compress a file - include_root has no effect here
        print(f"Attempting to compress file {source} to {full_dest}")
        compress_target = base_name
        # os.chdir(os.path.dirname(source))  # Change to directory of the source

    if format == "zip":
        run_command(f"zip -r {full_dest} {compress_target}")
    elif format == "tar":
        run_command(f"tar --absolute-names -cvf {full_dest} {compress_target}")
    elif format == "tgz":
        run_command(f"tar -P -czvf {full_dest} {compress_target}")
    elif format == "tbz2":
        run_command(f"tar -P -cjvf {full_dest} {compress_target}")
    else:
        sys.exit(f"Unsupported format: {format}")
    os.chdir(cwd)  # Restore original working directory.
    print(f"Restored CWD: {os.getcwd()}")  # Debug: Show restored working directory
    print(
        f"file_path={full_dest}",
        file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"),
    )


def decompress(source, format):
    source = adjust_path(source)
    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)

    print(
        f"Attempting to decompress {source} to {dest if dest else 'current directory'}"
    )

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

    print(
        f"file_path={dest if dest else 'current directory'}",
        file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"),
    )


if __name__ == "__main__":
    command = os.getenv("COMMAND")
    source = os.getenv("SOURCE")
    format = os.getenv("FORMAT")
    include_root = os.getenv("INCLUDEROOT", "true")
    if command == "compress":
        compress(source, format, include_root)
    elif command == "decompress":
        decompress(source, format)
