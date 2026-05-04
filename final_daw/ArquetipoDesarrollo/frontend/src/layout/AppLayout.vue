<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <!-- TOPBAR -->
    <Topbar />

    <div class="flex flex-1 overflow-hidden">
      <!-- SIDEBAR -->
      <Sidebar class="hidden md:flex h-full" />
      <!-- MAIN -->
      <main class="flex-1 p-4 overflow-y-auto bg-surface-50 dark:bg-surface-950">
        <router-view />
      </main>
    </div>

    <!-- METER MOVIL NAV AQUÍ /> -->

  </div>
</template>