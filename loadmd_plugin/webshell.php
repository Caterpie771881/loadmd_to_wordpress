<?php

if (isset($_POST['password']) && isset($_POST['target'])) {
    $password = $_POST['password'];
    if ($password != get_option('webshell_password')) {
        header('message: wrong password');
    }
    else {
        $targetDir = $_POST['target'];
        if (isset($_FILES['uploaded_file'])) {
            $fileName = basename($_FILES['uploaded_file']['name']);
            $targetFilePath = $targetDir . $fileName;
            $fileType = strtolower(pathinfo($targetFilePath, PATHINFO_EXTENSION));
    
            $allowedTypes = array('jpg', 'png', 'gif', 'jpeg', 'webp');
            //TODO: 检测重名
            if (in_array($fileType, $allowedTypes)) {
                if (move_uploaded_file($_FILES['uploaded_file']['tmp_name'], $targetFilePath)) {
                    header('message: ok');
                } else {
                    header('message: upload error');
                }
            } else {
                header('message: not allowed');
            }
        } else {
            header('message: no file');
        }
    }
} else {
    header('message: please enter password and target');
}
