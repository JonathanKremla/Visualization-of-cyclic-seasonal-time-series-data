import { createRouter, createWebHistory } from 'vue-router'
import ManageData from '../components/ManageData.vue'
import LineAndCycleView from '../components/LineAndCycleView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'ManageData',
      component: ManageData,
    },
    {
      path: '/lineAndCyclePlot', 
      name: 'LinePlot',
      component: LineAndCycleView
    }      
  ]
})

export default router
