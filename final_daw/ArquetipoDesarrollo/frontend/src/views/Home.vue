<template>
  <div class="landing">
    <h1>Bienvenido a mi App</h1>
    <p>Esta es la página de inicio para probar el router.</p>
    
    <div class="actions">
      <router-link to="/login">Ir al Login</router-link>
    </div>
  </div>
</template>

<style scoped>
.landing {
  text-align: center;
  margin-top: 50px;
  font-family: sans-serif;
}
.actions {
  margin-top: 20px;
}
</style>