import React from 'react';
import { deleteUser } from 'aws-amplify/auth';

function Header({ signOut }) {
    const handleDeleteAccount = async () => {
        try {
            if(window.confirm("¿Está seguro que desea eliminar su cuenta?"))
                await deleteUser();
                alert("Cuenta eliminada, vuelva pronto!")
        } catch (error) {
            console.log(error);
        }
    }

    return (
        <header id="AppHeader">
        <h1 id='header-h1'>Educ App SD</h1>
        <button onClick={signOut} id="logoutbutton">Cerrar Sesión</button>
        <button onClick={handleDeleteAccount} id="deleteaccount">¿Desea Eliminar su Cuenta?</button>
        </header>
    );
}

export default Header;