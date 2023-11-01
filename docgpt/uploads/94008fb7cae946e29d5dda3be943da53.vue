<template>
  <v-main>
    <v-container class="pa-0 h-100 d-flex justify-center align-center" fluid>
      <v-row class="AuthLayout mt-0 mb-0 h-100 w-100">
        <v-col class="pa-0 d-none side d-md-block" cols="10" md="3" lg="4">
          <div class="AuthLayout__side h-100"></div>
        </v-col>
        <v-col class="pa-0 pd-md-auto d-flex align-center justify-center" cols="11" sm="" md="9" lg="8">
          <div class="AuthLayout__main d-flex justify-center align-center w-50 h-100 ma-auto">
            <slot />
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<style scoped>
.AuthLayout__side {
  background-image: url('src/assets/home_side.jpg');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
}

@media only screen and (max-width: 1100px) {
  .AuthLayout__main {
    width: 65% !important;
  }
}

@media only screen and (max-width: 700px) {
  .AuthLayout__main {
    width: 100% !important;
    height: 75% !important;
  }
}

@media only screen and (max-height: 800px) {
  .AuthLayout__main {
    width: 100% !important;
    height: 100% !important;
  }
}
</style>
