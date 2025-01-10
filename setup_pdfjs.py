import os 
import subprocess 
import shutil


# update this value to install a newer pdf.js version

PDFJS_VERSION = "v4.10.38"

PDFJS_REPO = "https://github.com/mozilla/pdf.js"
LOCAL_DIR = "./local_pdfjs/pdf.js-4.10.38"
TEMP_DIR = "temp_pdfjs"
PUBLIC_DIR = "./app/public/pdfjs"


def clone_pdfjs_to_temp_dir():
    
    print_message(f"cloning pdf.js tag version: {PDFJS_VERSION}" )

    if os.path.exists(LOCAL_DIR):
        print_message( "using local clone" )
        shutil.copytree( LOCAL_DIR, TEMP_DIR, dirs_exist_ok=True )
    else:

        subprocess.run(
            [ "git", "clone", "--branch", PDFJS_VERSION, "--depth", "1", PDFJS_REPO, TEMP_DIR ],
            check=True
        )


def build_pdfjs_in_temp_dir():
    
    print_message( "building pdf.js" )

    subprocess.run( [ "npm", "install" ], cwd=TEMP_DIR, check=True )
    subprocess.run( [ "npx", "gulp", "generic" ], cwd=TEMP_DIR, check=True )


def copy_build_to_app_public(): 

    print_message(f"copying to {PUBLIC_DIR}" )

    if not os.path.exists(PUBLIC_DIR):
        os.makedirs( PUBLIC_DIR )

    build_dir = os.path.join( TEMP_DIR, "build")

    shutil.copytree( build_dir, os.path.join( PUBLIC_DIR, "build" ), dirs_exist_ok=True )


def delete_temp_dir():
    
    print_message(f"cleaning {TEMP_DIR}/" )

    shutil.rmtree( TEMP_DIR, ignore_errors=True )


def print_message(message, level="INFO"):
    print(f"\n[{level}] { message }\n" )


if __name__ == "__main__":
    
    try:

        clone_pdfjs_to_temp_dir()
        build_pdfjs_in_temp_dir()
        copy_build_to_app_public()

    finally:

        print_message( "finally" )
        delete_temp_dir()







