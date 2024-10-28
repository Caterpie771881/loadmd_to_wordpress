<div class="wrap">
    <h2>markdown_loader</h2>
    <form action="options.php" method="post">
        <?php settings_fields('md_loader'); ?>
        <table class="form-table">
            <tr valign="top">
                <th scope="row">
                    后门地址: 
                </th>
                <td>
                    <input type="text" name="webshell_address" id="webshell_address"
                    value="<?php echo get_option('webshell_address'); ?>"
                    style="width:100%;max_width:500px">
                </td>
                <td>
                    <button type="button" onclick="click_check_address_button()" id="check_address_button">check</button>
                </td>
            </tr>
            <tr valign="top">
                <th scope="row">
                    后门密码: 
                </th>
                <td>
                    <input type="password" name="webshell_password" id="webshell_password"
                    value="<?php echo get_option('webshell_password'); ?>"
                    style="width:100%;max_width:500px">
                </td>
                <td>
                    <button type="button" onclick="click_password_button()" id="password_button">show</button>
                </td>
            </tr>
        </table>
        <p class="submit">
            <input type="submit" class="button-primary" value="<?php _e('保存设置') ?>">
        </p>
    </form>
    <button type="button" class="button-primary" onclick="export_config()">导出配置文件</button>
</div>

<script>
    function click_password_button() {
        let type = document.getElementById('webshell_password').type;
        document.getElementById('webshell_password').type = type=='password'?'text':'password';
        document.getElementById('password_button').innerHTML = type=='password'?'hide':'show';
    }
    function click_check_address_button(params) {
        let address = document.getElementById('webshell_address').value;
        fetch(address)
        .then( (resp) => resp.headers )
        .then( (data) => {
            if ( data.get('message') == "please enter password and key" )
                alert('该地址能正常访问');
            else
                alert('似乎无法到达该地址, 请检查');
        } )
    }
    function export_config() {
        let config = {
            "path": "/path/for/markdown",
            "webshell": {
                "address": document.getElementById('webshell_address').value,
                "password": document.getElementById('webshell_password').value,
            },
            "img_src": "https://you_domain/myimgs/",
            "target": "/path/to/store/imgs",
            "support": {
                "img_type": [],
                "languages": [],
            },
            "restapi": {
                "website": "https://you_website",
                "user": "username",
                "token": "token",
            },
        };
        config = JSON.dumps(config);
        let a_tag = document.createElement('a');
        a_tag.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(config));
        a_tag.setAttribute('download', 'config.json');
        a_tag.style.display = 'none';
        document.body.appendChild(a_tag);
        a_tag.click();
        document.body.removeChild(a_tag);
    }
</script>