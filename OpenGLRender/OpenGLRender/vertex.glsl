attribute vec3 position;
attribute vec3 color;
attribute vec2 uv;

uniform mat4 projection;
uniform mat4 model;

varying vec3 fg_color;
varying vec2 TexCoord;

void main()
{
    fg_color = color;
    gl_Position = projection  * model * vec4(position, 1.0);

    TexCoord = uv;
}