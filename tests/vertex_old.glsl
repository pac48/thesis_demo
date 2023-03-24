#version 410
layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 col;
out vec3 fg_color;
void main () {
    fg_color = col;
    gl_Position = vec4(pos, 1.0f);
}