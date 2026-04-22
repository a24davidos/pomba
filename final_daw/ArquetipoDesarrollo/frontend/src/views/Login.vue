<template>
  <div>
    <h1 class="title">Login in the page</h1>
    <form action class="form" @submit.prevent="login">
      <label class="form-label" for="email">Email:</label>
      <input v-model="email" class="form-input" type="email" id="email" required placeholder="Email" />
      <label class="form-label" for="password">Password:</label>
      <input v-model="password" class="form-input" type="password" id="password" placeholder="Password" />
      <span v-show="error" style="color: red;"> Algo metiste mal </span>
      <input class="form-submit" type="submit" value="Login" />
    </form>
  </div>
</template>

<script>
  import { authService } from "@/api/auth";

  export default {
    data() {
      return {
        email: "",
        password: "",
        error: false
      }
    },
    methods: {
      async login() {
        try {
          const response = await authService.login(this.email, this.password);

          // Mandamos al usuario a la Home
          this.$router.push('/home');

        } catch (error) {
          //Si hay problema mostramos un mensaje
          this.error = true

        }
      }
    }
  };
</script>

<style scoped>
  .login {
    padding: 2rem;
  }

  .title {
    text-align: center;
  }

  .form {
    margin: 3rem auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 20%;
    min-width: 350px;
    max-width: 100%;
    background: rgba(19, 35, 47, 0.9);
    border-radius: 5px;
    padding: 40px;
    box-shadow: 0 4px 10px 4px rgba(0, 0, 0, 0.3);
  }

  .form-label {
    margin-top: 2rem;
    color: white;
    margin-bottom: 0.5rem;
  }

  /* equivalente a &:first-of-type */
  .form-label:first-of-type {
    margin-top: 0rem;
  }

  .form-input {
    padding: 10px 15px;
    background: none;
    background-image: none;
    border: 1px solid white;
    color: white;
  }

  /* equivalente a &:focus */
  .form-input:focus {
    outline: 0;
    border-color: #1ab188;
  }

  .form-submit {
    background: #1ab188;
    border: none;
    color: white;
    margin-top: 3rem;
    padding: 1rem 0;
    cursor: pointer;
    transition: background 0.2s;
  }

  /* equivalente a &:hover */
  .form-submit:hover {
    background: #0b9185;
  }
</style>