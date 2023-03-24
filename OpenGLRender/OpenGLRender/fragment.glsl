in vec3 fg_color;
in vec2 TexCoord;

uniform sampler2D textureSampler;

void main () {

    gl_FragColor = vec4(fg_color, 1.);
}