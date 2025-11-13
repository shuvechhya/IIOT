class dashboardNav {
  id = $state<string>("dashboard");
  value = $state<string>("Dashboard");

  change(id: string, value: string) {
    this.value = value;
    this.id = id;
  }
}

export const DashboardNav = new dashboardNav();
