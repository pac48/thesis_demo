attribute vec3 position;
attribute vec4 color;
attribute vec3 normal;
//attribute vec2 uv;

uniform mat4 projection;
uniform mat4 model;

varying vec4 fg_color;
//varying vec2 fg_texCoord;
varying vec3 fg_normal;

void main()
{
    fg_color = color;
    gl_Position = projection  * model * vec4(position, 1.0);

//    fg_texCoord = uv;
    fg_normal = mat3(model) * normal;
}