<?php
/*
Plugin Name: markdown 上传助手
Plugin URI: http://URI_Of_Page_Describing_Plugin_and_Updates
Description: 用于配合本地脚本进行 markdown 文章的上传
Version: 0.1
Author: caterpie
Author URI: 
License: GPLv2 or later
*/

/*  Copyright 2024  caterpie  (email : 1915036350@qq.com)

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

if ( !function_exists( 'add_action' ) ) {
	echo 'Hi there!  I\'m just a plugin, not much I can do when called directly.';
	exit;
}
// 初始化插件
function plugin_activation() {
    $characters = 'abcdefghijklmnopqrstuvwxyz';
    $password = '';
    for ($i = 0; $i < 10; $i++) {
        $password .= $characters[mt_rand(0, 25)];
    }
    $default_options = [
        'webshell_address' => 'Please set the address',
        'webshell_password' => $password,
    ];
    foreach ($default_options as $key => $value) {
        if (!get_option($key)) {
            add_option($key, $value);
        }
    }
}
register_activation_hook(__FILE__, 'plugin_activation');

// 注册 webshell 入口
function curPageURL() {
    $pageURL .= 'http';
    if ($_SERVER["HTTPS"] == "on") {
        $pageURL .= "s";
    }
    $pageURL .= "://";
    if ($_SERVER["SERVER_PORT"] != "80" && $_SERVER["SERVER_PORT"] != "443") {
        $pageURL .= $_SERVER["SERVER_NAME"].
        ":".$_SERVER["SERVER_PORT"].$_SERVER["REQUEST_URI"];
    } else {
        $pageURL .= $_SERVER["SERVER_NAME"].$_SERVER["REQUEST_URI"];
    }
    return $pageURL;
}
$current_url = curPageURL();
if ($current_url == get_option('webshell_address')) {
    include_once('webshell.php');
}

// 添加后台页面实现自定义设置
function add_setting_page() {
    add_menu_page(
        'md 上传助手',
        'md 上传助手',
        'manage_options',
        plugin_dir_path(__FILE__) . 'setting_page.php',
        null,
        null,
        20
    );
}
add_action('admin_menu', 'add_setting_page');
function register_my_settings() {
    register_setting('md_loader', 'webshell_address');
    register_setting('md_loader', 'webshell_password');
}
add_action('admin_init', 'register_my_settings');

// 卸载插件
function plugin_uninstall() {
    delete_option('webshell_address');
    delete_option('webshell_password');
}
register_uninstall_hook( __FILE__, 'plugin_uninstall' );