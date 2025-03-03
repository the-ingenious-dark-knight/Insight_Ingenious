import { writable } from 'svelte/store';
export const prerender = true
export async function _get_token(window: Window) {
    var token = writable(window.localStorage.getItem('token'))
    return token
}

export async function _set_token(window: Window, token: string) {
    var token = writable(window.localStorage.setItem('token', token))
    return token
}