#version 410 core



uniform vec3 lightDir;
//uniform sampler2D textureSampler;

varying vec4 fg_color;
//varying vec2 fg_texCoord;
varying vec3 fg_normal;

varying vec4 FragPos;

void main () {
//    gl_FragColor = fg_color;// vec4(fg_color, 1.);

//    vec4 texel = texture2D(textureSampler, fg_texCoord);
//
    vec3 lightDirection = normalize(lightDir);
    vec3 normal = normalize(fg_normal);
    float diffuse = max(dot(normal, -lightDirection), 0.2);
//    vec3 color = diffuse * vec3(fg_color * texel);
    vec3 color = diffuse * vec3(fg_color);
//    color = diffuse *vec3(fg_color);
//
    gl_FragColor = vec4(color, fg_color.w);
//    gl_FragColor = vec4(FragPos.z,FragPos.z,FragPos.z, 1.0);


}