import{y as a}from"./vendor-CmCdJidw.js";function S(t,e){window.dispatchEvent(new StorageEvent("storage",{key:t,newValue:e}))}const g=(t,e)=>{const o=JSON.stringify(e);window.localStorage.setItem(t,o),S(t,o)},u=t=>{window.localStorage.removeItem(t),S(t,null)},l=t=>window.localStorage.getItem(t),i=t=>(window.addEventListener("storage",t),()=>window.removeEventListener("storage",t)),f=()=>{throw Error("useLocalStorage is a client-only hook")};function w(t,e){const o=()=>l(t),n=a.useSyncExternalStore(i,o,f),c=a.useCallback(r=>{try{const s=typeof r=="function"?r(JSON.parse(n)):r;s==null?u(t):g(t,s)}catch(s){console.warn(s)}},[t,n]);return a.useEffect(()=>{l(t)===null&&typeof e<"u"&&g(t,e)},[t,e]),[n?JSON.parse(n):e,c]}function p(t){const[e,o]=a.useState(()=>t),n=a.useCallback(c=>o(typeof c=="boolean"?c:r=>!r),[]);return[e,n]}export{w as a,p as u};