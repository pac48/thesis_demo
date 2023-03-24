#version 410

layout (location = 0) in vec3 position;
layout(location = 1) in vec3 col;

uniform mat4 projection;
uniform mat4 model;
out vec3 fg_color;

//out vec2 TexCoord;

void main()
{
    fg_color = col;
    gl_Position = projection  * model * vec4(position, 1.0);
}