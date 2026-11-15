import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
const css=readFileSync(new URL('../src/css/workspace.css',import.meta.url),'utf8')
const tokens=Object.fromEntries([...css.matchAll(/--([a-z-]+):(#[a-f0-9]{6})/g)].map(m=>[m[1],m[2]]))
function luminance(hex){return hex.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0)}
function contrast(a,b){const values=[luminance(a),luminance(b)].sort((a,b)=>a-b);return (values[1]+.05)/(values[0]+.05)}
for(const [name,foreground,background] of [
  ['primary on paper',tokens.ink,tokens.paper],['secondary on paper',tokens.muted,tokens.paper],
  ['action text',tokens.ink,tokens.cream],['button text','#ffffff',tokens.forest],
  ['danger text',tokens.danger,'#fff1eb'],['warning text',tokens.amber,'#fff1cd'],
])test(`${name} reaches 7:1`,()=>assert.ok(contrast(foreground,background)>=7,`${name}: ${contrast(foreground,background)}`))
