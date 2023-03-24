#version 410
in vec3 fg_color;
out vec4 color;

void main () {
    color = vec4(fg_color, 1.);
}