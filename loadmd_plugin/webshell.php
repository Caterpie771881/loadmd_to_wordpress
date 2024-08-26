<?php

function run_webshell() {
    if ( !isset($_POST['password']) or !isset($_POST['key']) ) {
        return 'please enter password and key';
    }
    $password = $_POST['password'];
    $key = $_POST['key'];
    if ( !check_password($password, $key) ) {
        return 'authentication failed';
    }
    if ( !isset($_POST['command']) ) {
        return 'no command';
    }
    $command = $_POST['command'];
    switch ($command) {
        case 'check':
            return check_file();
            break;
        case 'save':
            return save_file();
            break;
        default:
            return "undefind command: '$command'";
    }
}

function check_password($password, $key) {
    $password = base64_decode(rc4(base64_decode($password), $key));
    $timestamp = explode('@', $password)[1];
    $password = base64_decode(explode('@', $password)[0]);
    if ( abs(time() - $timestamp) > 120 ) {
        return FALSE;
    }
    if ( $password != get_option('webshell_password') ) {
        return FALSE;
    }
    return TRUE;
}

function check_file() {
    if ( !isset($_POST['target']) ) {
        return 'please enter target';
    }
    $targetDir = $_POST['target'];
    if ( !isset($_POST['filename']) ) {
        return 'please enter filename';
    }
    $fileName = $_POST['filename'];
    $targetFilePath = $targetDir . $fileName;
    if (file_exists($targetFilePath)) {
        return 'exist';
    }
    return 'not exist';
}

function save_file() {
    if ( !isset($_POST['target']) ) {
        return 'please enter target';
    }
    $targetDir = $_POST['target'];
    if (isset($_FILES['uploaded_file'])) {
        $fileName = basename($_FILES['uploaded_file']['name']);
        $targetFilePath = $targetDir . $fileName;
        $fileType = strtolower(pathinfo($targetFilePath, PATHINFO_EXTENSION));
    
        $allowedTypes = array('jpg', 'png', 'gif', 'jpeg', 'webp');
        if (in_array($fileType, $allowedTypes)) {
            if (move_uploaded_file($_FILES['uploaded_file']['tmp_name'], $targetFilePath)) {
                return 'ok';
            }
            return 'upload error';
        }
        return 'not allowed';
    }
    return 'no file';
}

function rc4($data, $pwd) {
    $key[] = "";
    $box = array();
    $pwd_length = strlen($pwd);
    $data_length = strlen($data);
    $cipher = "";
    for ($i = 0; $i < 256; $i++) {
        $key[$i] = ord($pwd[$i % $pwd_length]);
        $box[$i] = $i;
    }
    for ($j = $i = 0; $i < 256; $i++) {
        $j = ($j + $box[$i] + $key[$i]) % 256;
        $tmp = $box[$i];
        $box[$i] = $box[$j];
        $box[$j] = $tmp;
    }
    for ($a = $j = $i = 0; $i < $data_length; $i++) {
        $a = ($a + 1) % 256;
        $j = ($j + $box[$a]) % 256;
        $tmp = $box[$a];
        $box[$a] = $box[$j];
        $box[$j] = $tmp;
        $k = $box[(($box[$a] + $box[$j]) % 256)];
        $cipher .= chr(ord($data[$i]) ^ $k);
    }
    return $cipher;
}
