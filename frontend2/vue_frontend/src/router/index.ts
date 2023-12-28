import { createRouter, createWebHistory } from 'vue-router'
import ManageData from '../components/ManageData.vue'
import LinePlotView from '../components/LinePlotView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'ManageData',
      component: ManageData,
    },
    {
      path: '/lineplot', 
      name: 'LinePlot',
      component: LinePlotView
    }      
  ]
})

export default router
