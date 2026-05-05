<template>
    <header>
        <Toolbar class="border-none bg-transparent! px-6 py-2">
            <template #start>
                <div class="flex items-center gap-2 ">
                    <div class="w-9 h-9 bg-primary rounded-lg flex items-center justify-center">
                        <i class="pi pi-cloud text-primary-contrast text-lg"></i>
                    </div>
                    <span class="hidden sm:inline text-xl font-bold tracking-tight">Placeholder</span>
                </div>
            </template>

<template #center>
    <div class="flex items-center w-full max-w-3xl px-4">
        
        <IconField class="w-full group">
            <InputIcon>
                <i class="pi pi-search text-surface-500 group-focus-within:text-surface-900 dark:group-focus-within:text-surface-0" />
            </InputIcon>
            
            <InputText
                placeholder="Buscar"
                class="w-full !py-3 !px-12 !border-none 
                       !rounded-xl transition-all duration-200
                       bg-surface-100 dark:bg-surface-800
                       hover:bg-surface-200 dark:hover:bg-surface-700
                       focus:bg-surface-0 dark:focus:bg-surface-900 
                       focus:shadow-[0_1px_1px_0_rgba(65,69,73,0.3),0_1px_3px_1px_rgba(65,69,73,0.15)]
                       dark:focus:shadow-[0_1px_3px_rgba(0,0,0,0.5)]"
            />

        </IconField>
    </div>
</template>

            <template #end>
                <div class="flex items-center gap-4 ">
                    <ThemeToggle />
                    <Button icon="pi pi-user" rounded severity="secondary" />
                </div>
            </template>
        </Toolbar>
    </header>

</template>


<script setup>
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>