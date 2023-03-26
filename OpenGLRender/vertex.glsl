#version 410 core

attribute vec3 position;
attribute vec4 color;
attribute vec3 normal;
//attribute vec2 uv;

uniform mat4 projection;
uniform mat4 model;

varying vec4 fg_color;
//varying vec2 fg_texCoord;
varying vec3 fg_normal;

out vec4 FragPos;

void main()
{
    fg_color = color;
    gl_Position = projection  * model * vec4(position, 1.0);
//    gl_Position =  vec4(position, 1.0);

    FragPos = gl_Position;

//    fg_texCoord = uv;
    fg_normal =  normal;
}