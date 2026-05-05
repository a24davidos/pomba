<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <!-- TOPBAR -->
    <Topbar />

    <div class="flex flex-1 overflow-hidden">
      <!-- SIDEBAR -->
      <Sidebar class="hidden md:flex h-full" />
      <!-- MAIN -->
      <main class="flex-1 p-4 overflow-y-auto bg-surface-0 dark:bg-surface-900 rounded-xl md:mr-4">
        <router-view />
      </main>
    </div>

    <!-- METER MOVIL NAV AQUÍ /> -->

  </div>
</template>