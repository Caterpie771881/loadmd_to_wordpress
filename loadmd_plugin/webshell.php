<?php

function run_webshell() {
    if ( !isset($_POST['password']) ) {
        return 'please enter password';
    }
    $password = $_POST['password'];
    if ( $password != get_option('webshell_password') ) {
        return 'wrong password';
    }
    if ( !isset($_POST['target']) ) {
        return 'please enter target';
    }
    $targetDir = $_POST['target'];
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

function check_file() {
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