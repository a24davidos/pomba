<template>
    <header>
        <Toolbar class="border-none bg-transparent! px-6 py-2">
            <template #start>
                <div class="flex items-center gap-2">
                    <div class="w-9 h-9 bg-primary rounded-lg flex items-center justify-center">
                        <i class="pi pi-bolt text-primary-contrast text-lg"></i>
                    </div>
                    <span class="hidden sm:inline text-xl font-bold tracking-tight">Placeholder</span>
                </div>
            </template>

            <template #end>
                <div class="flex items-center gap-4">
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