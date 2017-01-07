#******************************************************************************
#
# Copyright (C) 2017, Katharina Ceesay-Seitz, TU Wien
#
# Converts 3D .obj file to opengl vertices, textures and normal vertices arrays
# Input file must contain lines like this:
# v -0,25 0,25 0    ... for vertices
# vn 0,707106781186546 0 0,707106781186549 .... for normal vertices
# vt 0 0  ... for textures
#
# No other line should start with "v ", "vn " or "vt "
# , will be converted to .
# Output filename will be the same as the input filename but with extension .h
#******************************************************************************


import sys
from argparse import ArgumentParser
from os.path import exists

def parse_input_line(line):
    split_line = line.split(" ")
    # remove first element ("v")
    del split_line[0]
    # x y z of 1 vertex
    vertex = []
    # replace , by .
    # if it contains "E" we assume it is 0 (e.g 5,55E-17)
    for elem in split_line:
        coord = str(elem.rstrip('\n')).replace(",",".")
        # if "E" in coord:
            # coord = "0"            
        vertex.append(coord)
    #print vertex
    return vertex
    
# input_array = vertices, normals, textures
# type: 0...vertex, 1...tex, 2...normal
# x = vx/tx/nx
# y = vy/ty/ny
# z = vz/tz/nz
def construct_array(input_array, type,x,y,z):
    output_a = ""
    for coord in input_array[int(x[type])-1]:
        # convert it to float, cut off some digits behind the comma
        # output_a += str(round(float(coord),5)) + ","
        output_a += coord + ","
    output_a += "\n" 
    for coord in input_array[int(y[type])-1]:
        # output_a += str(round(float(coord),5)) + ","
        output_a += coord + ","
    output_a += "\n" 
    for coord in input_array[int(z[type])-1]:
        # output_a += str(round(float(coord),5)) + ","
        output_a += coord + ","
    output_a += "\n" 
    return output_a

################################# main ####################################

def obj2opengl(in_file):
    name = in_file.split(".")[0]
    f = open(in_file, 'r')
    f_out = open(name + ".h", 'w')

    f_out.write("/* created by obj2openglheader.py */") 
    f_out.write("\n\n")

    # 1 line per vertex [x,y,z]
    # it will be a 2 dimensional array
    vertices = []
    normals = []
    textures = []
    faces = []
    
    # construct input arrays
    for line in f:
        # store all vertices
        if line.startswith("v "):
            vertices.append(parse_input_line(line))
        # store all normal vertices
        if line.startswith("vn "):
            normals.append(parse_input_line(line))
        # store all textures
        if line.startswith("vt "):
            textures.append(parse_input_line(line))
        # store all faces
        if line.startswith("f"):
            faces.append(parse_input_line(line))
            
    # numVerts is length of faces*3
    f_out.write("unsigned int " + name + "NumVerts = " + str(len(faces)*3) + ";\n\n")

    # 1 face = 1 triangle:
    #3/3/3 1/1/1 2/2/2
    #vx/tx/nx vy/ty/ny vz/tz/nz

    # output pyramidVerts:
    #vx_x, vx_y, vx_z,
    #vy_x, vy_y, vy_z,
    #vz_x, vz_y, vz_z

    #example
      # // f 3/3/3 1/1/1 2/2/2
      # 0, 0, 0.25,
      # 0.25, -0.25, 0,
      # 0.25, 0, 0,
      
    output_verts = "float " + name + "Verts [] = {\n"
    output_tex = "float " + name + "TexCoords [] = {\n"
    output_normals = "float " + name + "Normals [] = {\n"
    for face in faces:
        # three points of the triangle
        x = face[0].split("/")
        y = face[1].split("/")
        z = face[2].split("/")
        # x[0] is index of vertex x
        # x[1] is index of texture for x
        # x[2] is index of normal vertex x
        
        # write vertices
        # vertices[x[0]] is the coordinates of vertex x
        output_verts += "// f " + face[0] + " " + face[1] + " " + face[2] + "\n"
        output_verts += construct_array(vertices,0,x,y,z)
        output_tex += "// f " + face[0] + " " + face[1] + " " + face[2] + "\n"
        output_tex += construct_array(textures,1,x,y,z)
        output_normals += "// f " + face[0] + " " + face[1] + " " + face[2] + "\n"
        output_normals += construct_array(normals,2,x,y,z)

    output_verts += "};\n\n";
    output_tex += "};\n\n";
    output_normals += "};\n\n";

    f_out.write(output_verts)
    f_out.write(output_normals)
    f_out.write(output_tex)

    f.close()
    f_out.close()

def _main():
    # Argument handling
    parser = ArgumentParser(description="Converts 3D object file to opengl arrays",
                            epilog='Example: %s --input ' % sys.argv[0])
    parser.add_argument("--input", type=str, required=True,
                        help="Input 3D obj file.")

    args = parser.parse_args()
    if not exists(args.input):
        sys.stderr.write("ERROR: Input file '%s' " % args.input +
                         "does not exist!\n")
        sys.exit(2)

    obj2opengl(args.input)

if __name__ == '__main__':
    _main()