<template>
  <div class="grid grid-cols-1 lg:grid-cols-[260px_1fr] grid-rows-[64px_1fr] min-h-screen w-full bg-surface-100 dark:bg-surface-950 gap-y-2 pt-2">

    <!-- TOPBAR -->
    <header class="col-span-1 lg:col-span-2 flex gap-2 items-center px-6 z-10">

      <!-- LOGO -->
      <div class="flex items-center lg:w-59 shrink-0">
        <div class="w-9 h-9 bg-primary rounded-lg flex items-center justify-center">
          <i class="pi pi-cloud text-primary-contrast text-lg"></i>
        </div>
      </div>

      <!-- BUSCADOR --> 
      <div class="flex-1 flex justify-start ml-1">
        <div class="w-full max-w-4xl">
          <IconField class="w-full group">
            <InputIcon>
              <i class="pi pi-search text-surface-500 group-focus-within:text-surface-900 dark:group-focus-within:text-surface-0 transition-colors duration-200" />
            </InputIcon>

            <InputText
              placeholder="Buscar"
              class="w-full py-3 px-12 border-none 
                    rounded-3xl transition-all duration-200
                    bg-surface-150 dark:bg-surface-800
                    hover:bg-surface-200 dark:hover:bg-surface-700
                    focus:bg-surface-0 dark:focus:bg-surface-900 
                    focus:shadow-[0_1px_1px_0_rgba(65,69,73,0.3),0_1px_3px_1px_rgba(65,69,73,0.15)]
                    dark:focus:shadow-[0_1px_3px_rgba(0,0,0,0.5)]"
            />
          </IconField>
        </div>
      </div>

      <!-- USUARIO Y TOOGLE -->
      <div class="flex items-center gap-3 shrink-0">
        <ThemeToggle />
        <Button icon="pi pi-user" rounded severity="secondary" variant="text" />
      </div>
    </header>

    <!-- SIDEBAR -->
    <aside class="hidden lg:block p-3">
      <Sidebar />
    </aside>

    <!-- MAIN -->
    <main class="p-6 overflow-x-hidden bg-surface-0 dark:bg-surface-900 rounded-2xl ml-3 mr-3">
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <router-view />
      </div>
    </main>

  </div>
</template>