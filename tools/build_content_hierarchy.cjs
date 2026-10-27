const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),data=JSON.parse(fs.readFileSync(path.join(root,'tools/content_hierarchy.json'),'utf8'));
const output='/* Source-guarded clinical ownership. Generated from tools/content_hierarchy.json. */\nwindow.ContentHierarchyData = '+JSON.stringify(data,null,2)+';\n';
const target=path.join(root,'assets/content-hierarchy-data.js');
if(process.argv.includes('--check')){if(fs.readFileSync(target,'utf8')!==output)throw Error('Hierarchy data needs regeneration');}
else fs.writeFileSync(target,output);
console.log('Hierarchy data: '+Object.values(data.references).reduce((n,a)=>n+a.length,0)+' references across '+Object.keys(data.references).length+' roadmaps.');
