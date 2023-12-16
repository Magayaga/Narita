# Narita - Web browser in the Philippines
# Copyright 2023 Cyril John Magayaga [cjmagayaga957@gmail.com]

import sys
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QTabWidget, QWidget, QVBoxLayout, QMessageBox, QLabel, QHBoxLayout, QSlider, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

class NaritaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.add_tab("https://www.google.com")

        # Status bar label for displaying the current URL
        self.status_label = QLabel()
        self.status_label.setOpenExternalLinks(True)
        self.statusBar().addWidget(self.status_label)

        # Create navigation bar
        navbar = QToolBar()
        navbar.setIconSize(QSize(32, 32)) 
        self.addToolBar(navbar)

        # New Tab button
        new_tab_btn = QAction(QIcon('icons/new_tab.png'), 'New Tab', self)
        new_tab_btn.triggered.connect(self.add_blank_tab)
        navbar.addAction(new_tab_btn)

        # Back button
        back_btn = QAction(QIcon('icons/back.png'), 'Back', self)
        back_btn.triggered.connect(self.current_browser.back)
        navbar.addAction(back_btn)

        # Forward button
        forward_btn = QAction(QIcon('icons/forward.png'), 'Forward', self)
        forward_btn.triggered.connect(self.current_browser.forward)
        navbar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction(QIcon('icons/reload.png'), 'Reload', self)
        reload_btn.triggered.connect(self.current_browser.reload)
        navbar.addAction(reload_btn)

        # Home button
        home_btn = QAction(QIcon('icons/home.png'), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("QLineEdit { border-radius: 5px; padding: 2px; }")
        navbar.addWidget(self.url_bar)

        # Go button
        go_btn = QAction(QIcon('icons/go.png'), 'Go', self)
        go_btn.triggered.connect(self.navigate_to_url)
        navbar.addAction(go_btn)

        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        navbar.addAction(about_action)

        # Set the central widget to the tab widget
        self.setCentralWidget(self.tabs)

        # Set the window properties
        self.showMaximized()

        self.zoom_slider = QSlider(Qt.Horizontal, self)
        self.zoom_slider.setRange(1, 300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        navbar.addWidget(self.zoom_slider)

        # Add the zoom slider to the toolbar
        navbar.addWidget(self.zoom_slider)

    def add_blank_tab(self):
        self.add_tab()

    def add_tab(self, url="about:blank"):
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))

        # Create a new tab and set its layout
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(browser)

        # Add the tab to the tab widget
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)

        # Store the browser instance as a tab property
        tab.browser = browser

        # Connect the urlChanged signal to update the URL bar
        browser.urlChanged.connect(lambda q, tab=tab: (self.update_url_bar(q, tab), self.update_status_bar(q)))

        # Connect the titleChanged signal to update the tab title
        browser.titleChanged.connect(lambda title, index=index: self.update_tab_title(title, index))

        # Connect the contextMenuRequested signal to show_custom_context_menu
        browser.setContextMenuPolicy(Qt.CustomContextMenu)
        browser.customContextMenuRequested.connect(self.show_custom_context_menu)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.tabs.clear()
            self.add_tab("about:blank")

    def navigate_home(self):
        self.current_browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        input_text = self.url_bar.text()

        try:
            q = QUrl.fromUserInput(input_text)
            
            if q.scheme() == "":
                # If no scheme is provided, assume it's a direct URL
                q = QUrl("http://" + input_text)
            
            self.current_browser.setUrl(q)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error navigating to URL: {str(e)}")

    def update_url_bar(self, q, tab):
        if tab == self.tabs.currentWidget():
            self.url_bar.setText(q.toString())
    
    def update_status_bar(self, q):
        self.status_label.setText(f"Current URL: <a href='{q.toString()}'>{q.toString()}</a>")

    def update_tab_title(self, title, index):
        if index >= 0 and index < self.tabs.count():
            self.tabs.setTabText(index, title)

    @property
    def current_browser(self):
        return self.tabs.currentWidget().browser

    def show_about_dialog(self):
        about_text = (
            "<html>"
            "<body align='center'>"
            "<h2><img src='icons/narita.png' alt='Narita Logo'> Narita</h2>"
            "<p>Narita is a free and open-source web browser created and developed by <a href='https://github.com/magayaga'>Cyril John Magayaga</a></p>"
            "<p>latest release: v0.1-preview0 / December 3, 2023</p>"
            "</body>"
            "</html>"
        )

        about_dialog = QMessageBox()
        about_dialog.setWindowTitle("About Narita")

        # Set a pixmap for the logo
        logo_pixmap = QPixmap("icons/narita.png")
        about_dialog.setIconPixmap(logo_pixmap)

        # Set the HTML text for the about dialog
        about_dialog.setText(about_text)

        # Show the about dialog
        about_dialog.exec_()
    
    def update_zoom(self):
        self.current_browser.setZoomFactor(self.zoom_slider.value() / 100.0)
    
    def show_custom_context_menu(self, point):
        menu = self.current_browser.page().createStandardContextMenu()

        # Add custom actions to the context menu
        share_action = menu.addAction("Share")
        share_action.triggered.connect(self.share_link)

        copy_link_action = menu.addAction("Copy Link")
        copy_link_action.triggered.connect(self.copy_link)

        save_page_action = menu.addAction("Save Page As")
        save_page_action.triggered.connect(self.save_page_as)

        menu.exec_(self.current_browser.mapToGlobal(point))

    def share_link(self):
        # Implement the functionality for the "Share" action
        QMessageBox.information(self, "Share", "Implement Share functionality here.")

    def copy_link(self):
        # Implement the functionality for the "Copy Link" action
        link = self.current_browser.url().toString()
        QApplication.clipboard().setText(link)
        QMessageBox.information(self, "Copy Link", f"Link copied to clipboard:\n{link}")

    def save_page_as(self):
        # Get the current page's HTML content
        page = self.current_browser.page()
        page.toHtml(self.handle_html_content)

    def handle_html_content(self, html_content):
        # Ask the user for the file name and location
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Page As", "", "HTML Files (*.html);;All Files (*)", options=options)

        if file_name:
            # Save the HTML content to the specified file
            try:
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(html_content)
                QMessageBox.information(self, "Save Page As", f"Page saved to:\n{file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Save Page As", f"Error saving page: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Narita")
    window = NaritaBrowser()
    app.exec_()
