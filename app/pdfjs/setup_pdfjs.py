import os 
import sys 
import subprocess 
import shutil


# update this value to install a newer pdf.js version

PDFJS_VERSION = "v4.10.38"

PDFJS_REPO = "https://github.com/mozilla/pdf.js"

LOCAL_DIR = "./local_pdfjs/pdf.js-4.10.38"
TEMP_DIR = "./temp_pdfjs"
PUBLIC_DIR = "../public/pdfjs"
CUSTOM_CSS_PATH = "./custom_viewer.css"



def clone_pdfjs_to_temp_dir():
    
    print_message(f"cloning pdf.js tag version: \t {PDFJS_VERSION}" )

    if os.path.exists(LOCAL_DIR):
        print_message( "using local clone" )
        shutil.copytree( LOCAL_DIR, TEMP_DIR, dirs_exist_ok=True )
    else:
        subprocess.run(
            [ "git", "clone", "--branch", PDFJS_VERSION, "--depth", "1", PDFJS_REPO, TEMP_DIR ],
            check=True
        )



def build_pdfjs_in_temp_dir():
    
    print_message( "building pdf.js", newline_after=True )

    subprocess.run( [ "npm", "install" ], cwd=TEMP_DIR, check=True )
    subprocess.run( [ "npx", "gulp", "generic" ], cwd=TEMP_DIR, check=True )




def delete_unnecessary_files():

    print_message( "deleting unnecessary files", newline_before=True)

    files_to_delete = [
        os.path.join( TEMP_DIR, "build", "generic", "web", "compressed.tracemonkey-pldi-09.pdf" ),
        os.path.join( TEMP_DIR, "build", "generic", "web", "viewer.mjs.map" ),
        os.path.join( TEMP_DIR, "build", "generic", "build", "pdf.mjs.map" ),
        os.path.join( TEMP_DIR, "build", "generic", "build", "pdf.worker.mjs.map" ),
        os.path.join( TEMP_DIR, "build", "generic", "build", "pdf.sandbox.mjs.map" ),
    ]

    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            print_message(f"file deleted: {file_path}" )
        else:
            print_message(f"file to delete not found: {file_path}", level="WARN" )



def copy_build_to_app_public(): 

    print_message(f"copying to {PUBLIC_DIR}" )

    if os.path.exists(PUBLIC_DIR):
        print_message(f"deleting exsisting {PUBLIC_DIR} ")
        shutil.rmtree(PUBLIC_DIR)

    os.makedirs( PUBLIC_DIR )

    shutil.copytree( os.path.join( TEMP_DIR, "build"), os.path.join( PUBLIC_DIR, "build"), dirs_exist_ok=True )



def append_custom_css():

    print_message("appending custom css to viewer.css")

    viewer_css_path = os.path.join( PUBLIC_DIR, "build", "generic", "web", "viewer.css" )

    if os.path.exists(viewer_css_path) and os.path.exists(CUSTOM_CSS_PATH):
        with open(viewer_css_path, "a") as viewer_css_file, open(CUSTOM_CSS_PATH, "r") as custom_css_file:
            shutil.copyfileobj(custom_css_file, viewer_css_file)  # appends 
            print_message("custom css applied successfully")
    else:
        if not os.path.exists(viewer_css_path):
            print_message(f"viewer.css file not found at: {viewer_css_path}", level="ERROR")
        if not os.path.exists(CUSTOM_CSS_PATH):
            print_message(f"custom css file not found at: {CUSTOM_CSS_PATH}", level="ERROR")
    


def delete_temp_dir():
    print_message(f"deleting: {TEMP_DIR}/" )
    shutil.rmtree( TEMP_DIR, ignore_errors=True )



def print_message(message, level="INFO", newline_before=False, newline_after=False):
    if newline_before:
        print()
    print(f"[{level}] { message }" )
    if newline_after:
        print()





if __name__ == "__main__":

    print_message("starting PDF.js setup", newline_before=True, newline_after=True)
    
    try:

        clone_pdfjs_to_temp_dir()
        build_pdfjs_in_temp_dir()
        delete_unnecessary_files()
        copy_build_to_app_public()
        append_custom_css()

    except Exception as e:

        print_message(f"An error occured: {e}", level="ERROR")
        sys.exit(1)

    finally:

        print_message( "finally" )
        delete_temp_dir()
        print_message("PDF.js setup complete", newline_before=True, newline_after=True)

    sys.exit(0)





